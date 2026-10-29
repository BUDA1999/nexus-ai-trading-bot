"""Backtest offline educativo em CSV; sem conexão ao broker."""
import argparse
import csv
from dataclasses import dataclass
from core import Candle, filter_signal, position_size

@dataclass
class Trade:
    side: str
    entry_time: str
    exit_time: str
    pnl: float
    reason: str

def run(path, balance=10000.0, risk=0.005, max_spread=0.0003, contract_size=1.0):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    required = {"time", "open", "high", "low", "close", "signal", "trend", "spread", "atr"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError("CSV precisa de time,open,high,low,close,signal,trend,spread,atr")
    equity, trades, pending, pos = balance, [], None, None
    for r in rows:
        c = Candle(*(float(r[k]) for k in ("open", "high", "low", "close")))
        spread, av = float(r["spread"]), float(r["atr"])
        if pending and not pos:
            side, source = pending
            entry = c.open + spread/2 if side == "BUY" else c.open - spread/2
            dist = source * 1.5
            stop = entry - dist if side == "BUY" else entry + dist
            target = entry + dist*2 if side == "BUY" else entry - dist*2
            lots = position_size(equity, risk, entry, stop, contract_size, .01, 1.0)
            if lots: pos = [side, entry, stop, target, lots, r["time"]]
            pending = None
        if pos:
            side, entry, stop, target, lots, start = pos
            hit_sl = c.low <= stop if side == "BUY" else c.high >= stop
            hit_tp = c.high >= target if side == "BUY" else c.low <= target
            if hit_sl or hit_tp:
                # Conservador: se stop e alvo tocam na mesma vela, escolhe stop.
                reason = "SL" if hit_sl else "TP"
                exit_price = (stop if hit_sl else target) + (-spread/2 if side == "BUY" else spread/2)
                pnl = (exit_price-entry)*(1 if side == "BUY" else -1)*lots*contract_size
                equity += pnl; trades.append(Trade(side, start, r["time"], pnl, reason)); pos = None
        if not pos and not pending and r["signal"].upper() in {"BUY", "SELL"}:
            d = filter_signal(r["signal"], r["trend"].upper(), av, c.close, c.close+spread, spread, max_spread)
            if d.action in {"BUY", "SELL"}: pending = (d.action, av)
    if pos:
        side, entry, stop, target, lots, start = pos
        last = rows[-1]; close = float(last["close"]); spread = float(last["spread"])
        exit_price = close-spread/2 if side == "BUY" else close+spread/2
        pnl = (exit_price-entry)*(1 if side == "BUY" else -1)*lots*contract_size
        equity += pnl; trades.append(Trade(side, start, last["time"], pnl, "FIM_DADOS"))
    return trades, equity

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("csv"); p.add_argument("--balance", type=float, default=10000)
    p.add_argument("--risk", type=float, default=.005); p.add_argument("--max-spread", type=float, default=.0003)
    p.add_argument("--contract-size", type=float, default=1.0); a=p.parse_args()
    trades, end = run(a.csv, a.balance, a.risk, a.max_spread, a.contract_size)
    print(f"Operações: {len(trades)} | saldo inicial: {a.balance:.2f} | saldo final: {end:.2f}")
    for t in trades: print(f"{t.entry_time} {t.side} -> {t.exit_time} {t.reason}: PnL {t.pnl:.2f}")
if __name__ == "__main__": main()
