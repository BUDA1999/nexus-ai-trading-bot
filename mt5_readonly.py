"""Adaptador opcional de leitura para MT5; não contiene place_order/send calls."""
from __future__ import annotations

class AdapterUnavailable(RuntimeError):
    pass

def load_mt5():
    try:
        import MetaTrader5 as mt5
    except ImportError as exc:
        raise AdapterUnavailable("Instala MetaTrader5 apenas em Windows com terminal MT5; o núcleo não depende dele") from exc
    return mt5

def read_closed_rates(symbol: str, timeframe: int, count: int = 100):
    """Lê candles do MT5 e exclui a vela em formação. Uso apenas leitura."""
    if count < 2:
        raise ValueError("count deve ser >= 2")
    mt5 = load_mt5()
    if not mt5.initialize():
        raise AdapterUnavailable(f"Falha ao iniciar MT5: {mt5.last_error()}")
    try:
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count + 1)
        if rates is None or len(rates) < count:
            raise AdapterUnavailable(f"Histórico insuficiente: {mt5.last_error()}")
        return rates[:-1][-count:]
    finally:
        mt5.shutdown()
