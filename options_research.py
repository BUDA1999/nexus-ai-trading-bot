"""Black-Scholes básico para estudo de opções europeias; sem dados/execução."""
from __future__ import annotations
from math import erf, exp, log, pi, sqrt

def _cdf(x: float) -> float:
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))

def black_scholes(spot: float, strike: float, years: float, rate: float,
                  volatility: float, kind: str = "call") -> float:
    """Preço teórico sem dividendos; não serve para opções americanas."""
    if spot <= 0 or strike <= 0 or years <= 0 or volatility <= 0:
        raise ValueError("spot, strike, years e volatility devem ser positivos")
    kind = kind.lower()
    if kind not in {"call", "put"}:
        raise ValueError("kind deve ser call ou put")
    d1 = (log(spot / strike) + (rate + volatility * volatility / 2) * years) / (volatility * sqrt(years))
    d2 = d1 - volatility * sqrt(years)
    if kind == "call":
        return spot * _cdf(d1) - strike * exp(-rate * years) * _cdf(d2)
    return strike * exp(-rate * years) * _cdf(-d2) - spot * _cdf(-d1)
