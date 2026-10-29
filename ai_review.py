"""Contrato isolado para revisão por IA; implementação padrão não chama rede."""
from dataclasses import dataclass
from core import Decision

@dataclass(frozen=True)
class Review:
    approved_for_paper: bool
    explanation: str

class SignalReviewer:
    """O revisor nunca pode executar operações nem substituir limites de risco."""
    def review(self, decision: Decision) -> Review:
        if decision.action not in {"BUY", "SELL"}:
            return Review(False, "Não há sinal elegível para simulação")
        if decision.entry is None or decision.stop is None or decision.target is None:
            return Review(False, "Sinal sem níveis completos de risco")
        return Review(True, "Apenas elegível para paper trading; aprovação não é recomendação")
