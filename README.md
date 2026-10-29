# Nexus AI Trading Bot

Protótipo de estudo modular: sinais de visão + contexto MT5, filtros de risco, backtesting offline, monitorização e módulos de pesquisa. **Não envia ordens reais e não é aconselhamento financeiro.**

## Módulos (ficheiros na raiz por enquanto)
- `core.py`: EMA, ATR, validação de sinal e posição de risco.
- `backtest.py`: simulação offline de CSV (usa `core.py`).
- `strategies.py`: proposta sinal+tendência e níveis GRID apenas para pesquisa.
- `ai_review.py`: revisão local, sem LLM externo nem capacidade de executar ordens.
- `monitoring.py`: auditoria JSONL e métricas simples.
- `mt5_readonly.py`: adaptador opcional de leitura de velas fechadas.
- `options_research.py`: Black-Scholes educativo para opções europeias.
- `REFERENCIAS.md`: projetos avaliados, licenças e decisões.

## Testar localmente
Python 3.10+; testes principais sem dependências externas.

```bash
python -m unittest discover -s . -p 'test_*.py' -v
python backtest.py sample_signals.csv --balance 10000 --risk 0.005
```

O CSV de exemplo é artificial e não representa desempenho real. A integração MT5 requer Windows e terminal desktop; o adaptador é somente leitura. Android pode ser um painel de consulta/alertas no futuro, mas não substitui o terminal MT5.

Backtests não incluem todos os custos nem garantem desempenho. Manter teste em histórico fora da amostra e demo; não colocar passwords/tokens no GitHub.
