"""Auditoria local de sinais/paper trades e métricas simples; sem segredos."""
from __future__ import annotations
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

@dataclass(frozen=True)
class Event:
    kind: str
    timestamp: str
    payload: dict

    @classmethod
    def now(cls, kind: str, payload: dict) -> "Event":
        return cls(kind, datetime.now(timezone.utc).isoformat(), payload)

class JsonlAuditLog:
    """Append-only JSONL audit. Caller must omit account IDs/passwords/API keys."""
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: Event) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(event), ensure_ascii=False, allow_nan=False) + "\n")

@dataclass(frozen=True)
class Summary:
    count: int
    wins: int
    losses: int
    net_pnl: float
    max_drawdown: float
    win_rate: float

def summarize_pnls(pnls: Iterable[float]) -> Summary:
    values = list(pnls)
    equity = peak = drawdown = 0.0
    for pnl in values:
        if not isinstance(pnl, (int, float)):
            raise ValueError("PnL deve ser numérico")
        equity += pnl
        peak = max(peak, equity)
        drawdown = max(drawdown, peak - equity)
    wins = sum(p > 0 for p in values)
    losses = sum(p < 0 for p in values)
    return Summary(len(values), wins, losses, sum(values), drawdown,
                   wins / len(values) if values else 0.0)
