"""Backtest educativo sobre CSV já exportado/rotulado; não liga ao broker."""
from __future__ import annotations
import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional
from .core import Candle, filter_signal, position_size


@dataclass(frozen=True)
class Row:
    time: str
    candle: Candle
    signal: str
    trend: str
    spread: float
    atr: float


@dataclass
class Trade:
    side: str
    entry_time: str
    exit_time: str
    entry: float
    exit: float
    lots: float
    pnl: float
    reason: str


def load_csv(path: str | Path) -> list[Row]:
    rows: list[Row] = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required = {"time", "open", "high", "low", "close", "signal", "trend", "spread", "atr"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("CSV precisa de: time,open,high,low,close,signal,trend,spread,atr")
        for raw in reader:
            candle = Candle(*(float(raw[k]) for k in ("open", "high", "low", "close")))
            signal = raw["signal"].strip().upper()
            trend = raw["trend"].strip().upper()
            if signal not in {"BUY", "SELL", "NONE", ""} or trend not in {"UP", "DOWN", "FLAT"}:
                raise ValueError(f"Sinal/tendência inválido na linha {reader.line_num}")
            rows.append(Row(raw["time"], candle, signal, trend, float(raw["spread"]), float(raw["atr"])))
    rows.sort(key=lambda r: r.time)
    return rows


def run_backtest(rows: list[Row], balance: float = 10000.0, risk_fraction: float = 0.005,
                 max_spread: float = 0.0003, sl_atr: float = 1.5, reward_risk: float = 2.0,
                 contract_size: float = 1.0, lot_step: float = 0.01,
                 max_lots: float = 1.0) -> tuple[list[Trade], float]:
    """Sinais ao fecho; entrada na abertura seguinte. Se SL e TP tocam na mesma vela, assume SL primeiro."""
    if not 0 < risk_fraction <= 0.02:
        raise ValueError("risk_fraction deve estar entre 0 e 0.02")
    equity = balance
    open_pos: Optional[dict] = None
    trades: list[Trade] = []
    pending: Optional[tuple[Row, str]] = None
    for row in rows:
        # Executa a intenção anterior na abertura da vela atual, incluindo spread.
        if pending and open_pos is None:
            source, side = pending
            entry = row.candle.open + row.spread / 2 if side == "BUY" else row.candle.open - row.spread / 2
            dist = source.atr * sl_atr
            stop = entry - dist if side == "BUY" else entry + dist
            target = entry + dist * reward_risk if side == "BUY" else entry - dist * reward_risk
            lots = position_size(equity, risk_fraction, entry, stop, contract_size, lot_step, max_lots)
            if lots > 0:
                open_pos = {"side": side, "entry": entry, "stop": stop, "target": target,
                            "lots": lots, "time": row.time}
            pending = None
        if open_pos:
            pos = open_pos
            hi, lo = row.candle.high, row.candle.low
            exit_price, why = None, ""
            if pos["side"] == "BUY":
                if lo <= pos["stop"]: exit_price, why = pos["stop"] - row.spread / 2, "SL"
                elif hi >= pos["target"]: exit_price, why = pos["target"] - row.spread / 2, "TP"
            else:
                if hi >= pos["stop"]: exit_price, why = pos["stop"] + row.spread / 2, "SL"
                elif lo <= pos["target"]: exit_price, why = pos["target"] + row.spread / 2, "TP"
            if exit_price is not None:
                direction = 1 if pos["side"] == "BUY" else -1
                pnl = (exit_price - pos["entry"]) * direction * pos["lots"] * contract_size
                equity += pnl
                trades.append(Trade(pos["side"], pos["time"], row.time, pos["entry"], exit_price,
                                    pos["lots"], pnl, why))
                open_pos = None
        if open_pos is None and pending is None and row.signal in {"BUY", "SELL"}:
            d = filter_signal(row.signal, row.trend, row.atr, row.candle.close,
                              row.candle.close + row.spread, row.spread, max_spread, sl_atr, reward_risk)
            if d.action in {"BUY", "SELL"}:
                pending = (row, d.action)
    if open_pos:
        # Marca a mercado no último fecho; nenhuma posição é deixada silenciosamente aberta.
        last = rows[-1]
        pos = open_pos
        exit_price = last.candle.close - last.spread / 2 if pos["side"] == "BUY" else last.candle.close + last.spread / 2
        direction = 1 if pos["side"] == "BUY" else -1
        pnl = (exit_price - pos["entry"]) * direction * pos["lots"] * contract_size
        equity += pnl
        trades.append(Trade(pos["side"], pos["time"], last.time, pos["entry"], exit_price,
                            pos["lots"], pnl, "FIM_DADOS"))
    return trades, equity


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("csv", help="CSV com candles e sinais/tendência previamente preparados")
    ap.add_argument("--balance", type=float, default=10000)
    ap.add_argument("--risk", type=float, default=0.005, help="fração por operação; máximo 0.02")
    ap.add_argument("--max-spread", type=float, default=0.0003)
    ap.add_argument("--contract-size", type=float, default=1.0)
    args = ap.parse_args()
    trades, ending = run_backtest(load_csv(args.csv), args.balance, args.risk,
                                  max_spread=args.max_spread, contract_size=args.contract_size)
    wins = sum(t.pnl > 0 for t in trades)
    print(f"Operações: {len(trades)} | ganhos: {wins} | perdas: {len(trades)-wins}")
    print(f"Saldo inicial: {args.balance:.2f} | saldo final: {ending:.2f} | retorno: {(ending/args.balance-1)*100:.2f}%")
    for t in trades:
        print(f"{t.entry_time} {t.side} -> {t.exit_time} {t.reason}: PnL {t.pnl:.2f}")

if __name__ == "__main__":
    main()
