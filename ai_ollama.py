"""Revisão consultiva local de sinais através da API de chat do Ollama.

O modelo recebe apenas dados resumidos do sinal e devolve comentário estruturado.
A decisão matemática de risco continua soberana; este módulo não acede ao MT5,
rede de corretoras, nem contém métodos de execução de ordens.
"""
from __future__ import annotations
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class AIReview:
    status: str  # REVIEW_ONLY ou UNAVAILABLE
    summary: str
    risks: tuple[str, ...]
    model: str

class ChatTransport(Protocol):
    def __call__(self, payload: dict) -> dict: ...

class OllamaReviewer:
    def __init__(self, model: str = "qwen2.5:3b", base_url: str = "http://localhost:11434",
                 timeout: float = 12.0, transport: ChatTransport | None = None):
        if not model.strip() or timeout <= 0:
            raise ValueError("modelo e timeout têm de ser válidos")
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.transport = transport or self._http_chat

    def _http_chat(self, payload: dict) -> dict:
        req = urllib.request.Request(
            self.base_url + "/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def review(self, *, signal: str, trend: str, confidence: float,
               spread_over_limit: bool, risk_percent: float, has_stop: bool) -> AIReview:
        """Devolve análise estruturada; falha fechada quando serviço/modelo falha."""
        signal = str(signal).upper().strip()
        trend = str(trend).upper().strip()
        # Evita mandar valores ilimitados ou texto arbitrário para o modelo.
        if signal not in {"BUY", "SELL", "WAIT"} or trend not in {"UP", "DOWN", "FLAT"}:
            return AIReview("UNAVAILABLE", "Entrada inválida; não considerar o sinal.", ("Dados fora do formato",), self.model)
        if not 0 <= confidence <= 1 or not 0 <= risk_percent <= 2:
            return AIReview("UNAVAILABLE", "Valores fora dos limites; não considerar o sinal.", ("Dados inválidos",), self.model)
        facts = {
            "signal": signal, "trend": trend,
            "confidence": round(confidence, 3),
            "spread_over_limit": bool(spread_over_limit),
            "risk_percent": round(risk_percent, 3), "stop_defined": bool(has_stop),
        }
        system = (
            "És um assistente de revisão educacional de sinais. Não dês recomendação financeira. "
            "Nunca inventes cotações, nunca alteres a decisão ou o risco, nunca sugiras remover stop. "
            "Aponta incompatibilidade sinal/tendência, spread, confiança baixa e ausência de stop. "
            "Responde APENAS JSON com summary string e risks array de strings. A resposta é só comentário, não aprovação para operar."
        )
        payload = {"model": self.model, "stream": False, "format": "json", "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(facts, separators=(",", ":"))},
        ], "options": {"temperature": 0}}
        try:
            data = self.transport(payload)
            content = data["message"]["content"]
            parsed = json.loads(content)
            summary = parsed.get("summary", "Revisão indisponível")
            risks = parsed.get("risks", [])
            if not isinstance(summary, str) or not isinstance(risks, list) or not all(isinstance(x, str) for x in risks):
                raise ValueError("formato da revisão inválido")
            risks = list(risks)
            # Regras determinísticas sempre acrescentadas: IA não as pode sobrepor.
            if signal == "BUY" and trend != "UP" or signal == "SELL" and trend != "DOWN":
                risks.append("Sinal não alinhado com a tendência; filtro determinístico deve bloquear")
            if spread_over_limit:
                risks.append("Spread excede o limite; não considerar entrada")
            if not has_stop:
                risks.append("Stop ausente; não considerar entrada")
            return AIReview("REVIEW_ONLY", summary[:500], tuple(dict.fromkeys(x[:200] for x in risks))[:8], self.model)
        except (OSError, urllib.error.URLError, TimeoutError, KeyError, TypeError, ValueError, json.JSONDecodeError):
            return AIReview("UNAVAILABLE", "IA indisponível; ignorar comentário e não abrir qualquer operação.",
                            ("Modelo local não respondeu corretamente",), self.model)

if __name__ == "__main__":
    reviewer = OllamaReviewer(model=os.getenv("OLLAMA_MODEL", "qwen2.5:3b"))
    print(reviewer.review(signal="WAIT", trend="FLAT", confidence=0, spread_over_limit=False,
                          risk_percent=0, has_stop=False))
