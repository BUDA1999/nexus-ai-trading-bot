"""Indicadores, filtros de sinal e dimensionamento de risco — sem ordens reais."""
from __future__ import annotations

from dataclasses import dataclass
from math import floor, isfinite
from typing import Iterable, Optional


@dataclass(frozen=True)
class Candle:
    open: float
    high: float
    low: float
    close: float

    def __post_init__(self) -> None:
        values = (self.open, self.high, self.low, self.close)
        if not all(isfinite(v) and v > 0 for v in values):
            raise ValueError("Preços OHLC devem ser finitos e positivos")
        if self.high < max(self.open, self.close, self.low) or self.low > min(self.open, self.close, self.high):
            raise ValueError("Vela OHLC inválida: high/low não contêm open/close")


def ema(values: Iterable[float], period: int) -> list[Optional[float]]:
    """EMA inicializada com SMA; valores antes do aquecimento são None."""
    xs = list(values)
    if period < 1:
        raise ValueError("period tem de ser >= 1")
    out: list[Optional[float]] = [None] * len(xs)
    if len(xs) < period:
        return out
    seed = sum(xs[:period]) / period
    out[period - 1] = seed
    alpha = 2.0 / (period + 1)
    current = seed
    for i in range(period, len(xs)):
        current = alpha * xs[i] + (1 - alpha) * current
        out[i] = current
    return out


def atr(candles: Iterable[Candle], period: int = 14) -> list[Optional[float]]:
    """ATR de Wilder. O primeiro valor requer period true ranges."""
    bars = list(candles)
    if period < 1:
        raise ValueError("period tem de ser >= 1")
    if not bars:
        return []
    trs: list[float] = []
    for i, bar in enumerate(bars):
        if i == 0:
            trs.append(bar.high - bar.low)
        else:
            prev = bars[i - 1].close
            trs.append(max(bar.high - bar.low, abs(bar.high - prev), abs(bar.low - prev)))
    out: list[Optional[float]] = [None] * len(bars)
    if len(trs) < period:
        return out
    value = sum(trs[:period]) / period
    out[period - 1] = value
    for i in range(period, len(trs)):
        value = ((period - 1) * value + trs[i]) / period
        out[i] = value
    return out


def classify_trend(closes: Iterable[float], period: int = 200, slope_bars: int = 10) -> str:
    """Tendência UP/DOWN/FLAT usando apenas fechos da última vela fechada."""
    xs = list(closes)
    if slope_bars < 1:
        raise ValueError("slope_bars tem de ser >= 1")
    series = ema(xs, period)
    i = len(xs) - 1
    prior = i - slope_bars
    if prior < 0 or series[i] is None or series[prior] is None:
        return "FLAT"
    now, then = series[i], series[prior]
    if xs[i] > now and now > then:
        return "UP"
    if xs[i] < now and now < then:
        return "DOWN"
    return "FLAT"


@dataclass(frozen=True)
class Decision:
    action: str  # BUY, SELL, WAIT
    reason: str
    entry: Optional[float] = None
    stop: Optional[float] = None
    target: Optional[float] = None


def filter_signal(vision_signal: Optional[str], trend: str, atr_value: float,
                  bid: float, ask: float, spread: float, max_spread: float,
                  sl_atr: float = 1.5, reward_risk: float = 2.0) -> Decision:
    """Converte candidato visual em sinal educativo; jamais envia uma ordem."""
    side = (vision_signal or "").strip().upper()
    if side not in {"BUY", "SELL"}:
        return Decision("WAIT", "Sem sinal visual direcional")
    if trend not in {"UP", "DOWN", "FLAT"}:
        return Decision("WAIT", "Tendência inválida")
    if trend == "FLAT" or (side == "BUY" and trend != "UP") or (side == "SELL" and trend != "DOWN"):
        return Decision("WAIT", "Sinal contra tendência ou tendência lateral")
    if not all(isfinite(x) for x in (atr_value, bid, ask, spread, max_spread, sl_atr, reward_risk)):
        return Decision("WAIT", "Dados de mercado inválidos")
    if atr_value <= 0 or bid <= 0 or ask < bid or spread < 0 or max_spread <= 0:
        return Decision("WAIT", "Dados de mercado inválidos")
    if spread > max_spread:
        return Decision("WAIT", "Spread acima do limite configurado")
    if sl_atr <= 0 or reward_risk <= 0:
        return Decision("WAIT", "Parâmetros de stop/risco inválidos")
    entry = ask if side == "BUY" else bid
    distance = atr_value * sl_atr
    stop = entry - distance if side == "BUY" else entry + distance
    target = entry + distance * reward_risk if side == "BUY" else entry - distance * reward_risk
    return Decision(side, "Filtros aprovados; sinal para simulação, não para execução", entry, stop, target)


def position_size(balance: float, risk_fraction: float, entry: float, stop: float,
                  contract_size: float = 1.0, lot_step: float = 0.01,
                  max_lots: float = 1.0) -> float:
    """Tamanho arredondado para baixo. contract_size deve refletir a moeda da conta."""
    vals = (balance, risk_fraction, entry, stop, contract_size, lot_step, max_lots)
    if not all(isfinite(v) for v in vals) or balance <= 0 or entry <= 0 or stop <= 0:
        return 0.0
    if not 0 < risk_fraction <= 0.02 or contract_size <= 0 or lot_step <= 0 or max_lots <= 0:
        return 0.0
    distance = abs(entry - stop)
    if distance <= 0:
        return 0.0
    raw_lots = balance * risk_fraction / (distance * contract_size)
    return min(max_lots, floor(raw_lots / lot_step) * lot_step)
