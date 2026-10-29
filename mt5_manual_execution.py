"""Envio manual e fortemente protegido de uma única ordem MT5.

DEMO por padrão. Nenhuma estratégia/IA chama este módulo. Para conta REAL,
exige opt-in por variável de ambiente, confirmação exata por ordem, validação
pre-trade do MT5 e limite rígido de risco. Não é aconselhamento financeiro.
"""
from __future__ import annotations
import os
from dataclasses import dataclass
from math import isfinite

LIVE_ENV = "NEXUS_ENABLE_LIVE_TRADING"
LIVE_VALUE = "I_ACCEPT_REAL_MONEY_RISK"
LIVE_MAX_RISK_PERCENT = 0.50

class ExecutionBlocked(RuntimeError):
    pass

@dataclass(frozen=True)
class ManualOrder:
    symbol: str
    side: str  # BUY / SELL
    volume: float
    stop_loss: float
    take_profit: float
    max_spread_points: int = 30
    risk_percent_limit: float = 0.25
    deviation_points: int = 20

@dataclass(frozen=True)
class ExecutionResult:
    status: str
    message: str
    ticket: int | None = None
    risk_percent: float | None = None


def required_confirmation(order: ManualOrder, is_live: bool) -> str:
    mode = "REAL" if is_live else "DEMO"
    return f"CONFIRM {mode} {order.symbol} {order.side.upper()} {order.volume:g}"


def _mt5_constant(mt5, name: str):
    if not hasattr(mt5, name):
        raise ExecutionBlocked(f"Constante MT5 indisponível: {name}")
    return getattr(mt5, name)


def send_manual_order(mt5, order: ManualOrder, confirmation: str, *, live_opt_in: str | None = None) -> ExecutionResult:
    """Valida e envia uma ordem market apenas após confirmação manual exata.

    Não chamar automaticamente a partir do YOLO ou do modelo de IA.
    ``mt5`` é o módulo MetaTrader5 oficial, importado pelo chamador.
    """
    side = order.side.upper().strip()
    if side not in {"BUY", "SELL"} or not order.symbol.strip():
        raise ExecutionBlocked("Símbolo/lado inválido")
    values = (order.volume, order.stop_loss, order.take_profit, order.risk_percent_limit)
    if not all(isfinite(x) for x in values) or order.volume <= 0 or order.stop_loss <= 0 or order.take_profit <= 0:
        raise ExecutionBlocked("Volume e níveis SL/TP devem ser positivos e finitos")
    if not 0 < order.risk_percent_limit <= LIVE_MAX_RISK_PERCENT:
        raise ExecutionBlocked(f"Limite por ordem deve ser >0 e <= {LIVE_MAX_RISK_PERCENT}%")
    if order.max_spread_points < 1 or order.deviation_points < 0:
        raise ExecutionBlocked("Limites de spread/desvio inválidos")

    account = mt5.account_info()
    if account is None:
        raise ExecutionBlocked(f"Sem sessão/conta MT5: {mt5.last_error()}")
    terminal = mt5.terminal_info() if hasattr(mt5, "terminal_info") else None
    if terminal is None or not getattr(terminal, "connected", False):
        raise ExecutionBlocked("Terminal MT5 sem ligação confirmada")
    if not getattr(terminal, "trade_allowed", False) or not getattr(account, "trade_allowed", False):
        raise ExecutionBlocked("Algo trading não está explicitamente permitido no terminal/conta")
    demo_mode = _mt5_constant(mt5, "ACCOUNT_TRADE_MODE_DEMO")
    real_mode = _mt5_constant(mt5, "ACCOUNT_TRADE_MODE_REAL")
    mode = getattr(account, "trade_mode", None)
    if mode == demo_mode:
        is_live = False
    elif mode == real_mode:
        is_live = True
        opt_in = live_opt_in if live_opt_in is not None else os.getenv(LIVE_ENV, "")
        if opt_in != LIVE_VALUE:
            raise ExecutionBlocked(f"Conta REAL bloqueada. Opt-in explícito necessário em {LIVE_ENV}; começa pela DEMO.")
    else:
        raise ExecutionBlocked("Tipo de conta MT5 desconhecido; ordem bloqueada")

    expected = required_confirmation(order, is_live)
    if confirmation.strip() != expected:
        raise ExecutionBlocked(f"Confirmação não corresponde. Escreve exatamente: {expected}")
    if is_live and order.risk_percent_limit > LIVE_MAX_RISK_PERCENT:
        raise ExecutionBlocked("Conta real excede o limite rígido de risco por ordem")

    info = mt5.symbol_info(order.symbol)
    if info is None:
        raise ExecutionBlocked(f"Símbolo MT5 desconhecido: {order.symbol}")
    if not getattr(info, "visible", False) and not mt5.symbol_select(order.symbol, True):
        raise ExecutionBlocked("Não foi possível selecionar o símbolo")
    info = mt5.symbol_info(order.symbol)
    if not info or not getattr(info, "trade_allowed", True):
        raise ExecutionBlocked("Negociação não permitida para este símbolo")
    tick = mt5.symbol_info_tick(order.symbol)
    if tick is None or tick.bid <= 0 or tick.ask < tick.bid:
        raise ExecutionBlocked("Cotação inválida ou indisponível")
    point = getattr(info, "point", 0.0)
    if not isinstance(point, (int, float)) or not isfinite(point) or point <= 0:
        raise ExecutionBlocked("Point size inválido para o símbolo")
    spread_points = (tick.ask - tick.bid) / point
    if spread_points > order.max_spread_points:
        raise ExecutionBlocked(f"Spread {spread_points:.1f} points excede limite {order.max_spread_points}")

    entry = tick.ask if side == "BUY" else tick.bid
    if (side == "BUY" and not order.stop_loss < entry < order.take_profit) or \
       (side == "SELL" and not order.take_profit < entry < order.stop_loss):
        raise ExecutionBlocked("Para BUY exige SL < preço < TP; para SELL exige TP < preço < SL")
    min_stop = getattr(info, "trade_stops_level", 0) * info.point
    if min_stop and min(abs(entry-order.stop_loss), abs(order.take_profit-entry)) < min_stop:
        raise ExecutionBlocked("SL/TP demasiado próximos segundo as regras do símbolo")

    vol_min = getattr(info, "volume_min", 0.0)
    vol_max = getattr(info, "volume_max", float("inf"))
    vol_step = getattr(info, "volume_step", 0.0)
    if vol_step <= 0 or order.volume < vol_min or order.volume > vol_max:
        raise ExecutionBlocked("Volume fora dos limites do símbolo")
    step_units = (order.volume - vol_min) / vol_step
    if abs(step_units - round(step_units)) > 1e-7:
        raise ExecutionBlocked("Volume não respeita o passo de lote permitido")

    positions = mt5.positions_get(symbol=order.symbol)
    if positions is None:
        raise ExecutionBlocked(f"Não foi possível verificar posições abertas: {mt5.last_error()}")
    if positions:
        raise ExecutionBlocked("Já há posição aberta neste símbolo; bloqueio anti-duplicação")
    if hasattr(mt5, "orders_get"):
        pending_orders = mt5.orders_get(symbol=order.symbol)
        if pending_orders is None:
            raise ExecutionBlocked(f"Não foi possível verificar ordens pendentes: {mt5.last_error()}")
        if pending_orders:
            raise ExecutionBlocked("Já há ordem pendente neste símbolo; bloqueio anti-duplicação")

    order_type = _mt5_constant(mt5, "ORDER_TYPE_BUY" if side == "BUY" else "ORDER_TYPE_SELL")
    pnl_at_stop = mt5.order_calc_profit(order_type, order.symbol, order.volume, entry, order.stop_loss)
    equity = getattr(account, "equity", 0.0)
    if pnl_at_stop is None or not isfinite(pnl_at_stop) or equity <= 0:
        raise ExecutionBlocked("MT5 não conseguiu estimar perda até ao stop")
    if pnl_at_stop >= 0:
        raise ExecutionBlocked("O nível indicado não representa perda segundo o cálculo MT5; ordem bloqueada")
    risk_cash = abs(pnl_at_stop)
    risk_percent = risk_cash / equity * 100
    if risk_percent > order.risk_percent_limit:
        raise ExecutionBlocked(f"Perda estimada no stop {risk_percent:.3f}% excede limite {order.risk_percent_limit:.3f}%")

    # symbol_info.filling_mode é bitmask SYMBOL_FILLING_*; não é o mesmo enum
    # de ORDER_FILLING_*. Mapeia só modos explicitamente suportados.
    flags = getattr(info, "filling_mode", 0)
    execution_mode = getattr(info, "trade_exemode", None)
    market_exec = getattr(mt5, "SYMBOL_TRADE_EXECUTION_MARKET", 2)
    if flags & getattr(mt5, "SYMBOL_FILLING_IOC", 2):
        filling = _mt5_constant(mt5, "ORDER_FILLING_IOC")
    elif flags & getattr(mt5, "SYMBOL_FILLING_FOK", 1):
        filling = _mt5_constant(mt5, "ORDER_FILLING_FOK")
    elif execution_mode != market_exec:
        filling = _mt5_constant(mt5, "ORDER_FILLING_RETURN")
    else:
        raise ExecutionBlocked("Símbolo não declara modo de preenchimento suportado")
    request = {
        "action": _mt5_constant(mt5, "TRADE_ACTION_DEAL"),
        "symbol": order.symbol,
        "volume": order.volume,
        "type": order_type,
        "price": entry,
        "sl": order.stop_loss,
        "tp": order.take_profit,
        "deviation": order.deviation_points,
        "magic": 20261029,
        "comment": "Nexus manual confirmed",
        "type_time": _mt5_constant(mt5, "ORDER_TIME_GTC"),
    }
    request["type_filling"] = filling
    checked = mt5.order_check(request)
    # MqlTradeCheckResult.retcode == 0 indica validação bem-sucedida;
    # DONE/PLACED são retcodes de order_send, não de order_check.
    if checked is None or getattr(checked, "retcode", None) != 0:
        raise ExecutionBlocked(f"MT5 order_check rejeitou a ordem: {getattr(checked, 'comment', mt5.last_error())}")

    # Uma única submissão; nunca repetir automaticamente em caso de resposta incerta.
    result = mt5.order_send(request)
    if result is None:
        raise ExecutionBlocked(f"Sem confirmação do servidor após order_send; verifica ordens no terminal antes de repetir: {mt5.last_error()}")
    accepted = {getattr(mt5, "TRADE_RETCODE_DONE", 10009), getattr(mt5, "TRADE_RETCODE_PLACED", 10008)}
    if getattr(result, "retcode", None) not in accepted:
        raise ExecutionBlocked(f"Servidor recusou ou não confirmou a ordem: {getattr(result, 'comment', '')}")
    return ExecutionResult("SUBMITTED", "Ordem submetida; confirma execução, volume e SL/TP no terminal MT5.",
                           getattr(result, "order", None), risk_percent)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Envio manual MT5. DEMO por padrão; sem aconselhamento financeiro.")
    parser.add_argument("--symbol", required=True); parser.add_argument("--side", choices=["BUY", "SELL"], required=True)
    parser.add_argument("--volume", type=float, required=True); parser.add_argument("--sl", type=float, required=True)
    parser.add_argument("--tp", type=float, required=True); parser.add_argument("--max-spread", type=int, default=30)
    parser.add_argument("--risk-limit", type=float, default=.25, help="limite por ordem em %% equity, máximo 0.5")
    args = parser.parse_args()
    import MetaTrader5 as mt5
    if not mt5.initialize():
        raise SystemExit(f"MT5 não inicializou: {mt5.last_error()}")
    try:
        order = ManualOrder(args.symbol, args.side, args.volume, args.sl, args.tp,
                            args.max_spread, args.risk_limit)
        account = mt5.account_info()
        is_live = account and account.trade_mode == getattr(mt5, "ACCOUNT_TRADE_MODE_REAL", -1)
        expected = required_confirmation(order, bool(is_live))
        print(f"Resumo: {order.side} {order.volume} {order.symbol}; SL={order.stop_loss}; TP={order.take_profit}; conta={'REAL' if is_live else 'DEMO'}")
        print("Isto não é aconselhamento financeiro. A IA não decide nem envia esta ordem.")
        confirmation = input(f"Para continuar, escreve exatamente '{expected}': ")
        result = send_manual_order(mt5, order, confirmation)
        print(result)
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    main()
