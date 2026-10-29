# Nexus AI Trading Bot — módulos integrados

Protótipo modular de estudo. Não envia ordens reais.

Os tópicos fornecidos eram páginas de descoberta e não repositórios únicos. Foram avaliados projetos de MT5, backtest, grid, monitorização e opções. Por segurança/licença, não copiámos nem executámos o código deles. Em vez disso, adicionámos implementações pequenas e próprias para pesquisa.

## Módulos incluídos nesta integração
- `core.py`: EMA, ATR, filtro de tendência/spread e risco.
- `strategies.py`: proposta visual+trend e níveis grid apenas para estudo, sem ordens.
- `ai_review.py`: interface local de revisão de sinais; nunca executa trades nem usa LLM externo.
- `monitoring.py`: logs de auditoria JSONL e métricas básicas.
- `mt5_readonly.py`: adaptador opcional de leitura de candles fechados no MT5.
- `options_research.py`: preço teórico Black-Scholes para opções europeias, isolado e sem corretora.
- `backtest.py`: simulação offline via CSV.

Todos estes arquivos estão na raiz do repositório por enquanto; a estrutura é plana para facilitar a consulta no GitHub. Python 3.10+ para o núcleo. MetaTrader5 Python package só funciona com terminal MT5 em Windows. Android pode ser uma app/painel de consulta depois, mas a execução de leitura MT5 deve ficar num PC Windows.

## Verificação local
Na pasta onde estiverem `core.py`, `monitoring.py`, `strategies.py`, `ai_review.py`, `options_research.py`, `mt5_readonly.py` e os testes:

```bash
python -m unittest discover -s . -p 'test_*.py' -v
```

Não introduzir passwords/chaves no código ou GitHub. Sem conta demo e limites de perda, não se faz paper-trading ligado ao broker.
