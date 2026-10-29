"""Propostas de estratégia para pesquisa. Nenhuma função envia ordens."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Proposal:
    side: str
    reason: str
    reference_price: float

class SignalStrategy:
    name = "base"
    def propose(self, *, price: float, trend: str, visual_signal: Optional[str] = None) -> Optional[Proposal]:
        raise NotImplementedError

class VisionTrendStrategy(SignalStrategy):
    """Sinal visual só é uma proposta; contexto direcional é um filtro obrigatório."""
    name = "vision-trend"
    def propose(self, *, price: float, trend: str, visual_signal: Optional[str] = None) -> Optional[Proposal]:
        side = (visual_signal or "").upper().strip()
        if side == "BUY" and trend == "UP":
            return Proposal("BUY", "Visão propõe compra e tendência é UP", price)
        if side == "SELL" and trend == "DOWN":
            return Proposal("SELL", "Visão propõe venda e tendência é DOWN", price)
        return None

@dataclass(frozen=True)
class GridLevel:
    side: str
    price: float

class GridResearch:
    """Gera níveis matemáticos de grelha para backtest; não cria ordens."""
    @staticmethod
    def levels(lower: float, upper: float, count: int) -> list[GridLevel]:
        if lower <= 0 or upper <= lower or count < 2:
            raise ValueError("Exige 0 < lower < upper e count >= 2")
        step = (upper - lower) / (count - 1)
        return [GridLevel("BUY" if i < count // 2 else "SELL", lower + i * step)
                for i in range(count)]
