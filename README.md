# Nexus AI Trading Bot

Protótipo modular de estudo: sinais, filtros de risco, IA consultiva e ferramentas para MT5. Inclui envio manual com salvaguardas; **não é aconselhamento financeiro, não garante lucro e não automatiza a decisão da IA**.

## Ficheiros
`core.py` e `backtest.py`: indicadores e backtest CSV. `ai_ollama.py`: comentário de sinais usando Ollama local. `strategies.py`: filtro de sinal e níveis de grelha apenas para pesquisa. `monitoring.py`: auditoria local. `options_research.py`: fórmula educativa de Black-Scholes. `mt5_readonly.py`: leitura de candles. `mt5_manual_execution.py`: envio de uma ordem market manual confirmada no MT5.

## Plataforma
Usar um **PC Windows** com terminal MetaTrader 5 (por exemplo XM demo). Android pode ser painel de observação/alertas no futuro; não executa diretamente o terminal MT5 desktop. IA fica local via Ollama.

## Testes
Python 3.10+; os testes não precisam de ligação ao broker:

```bash
python -m unittest discover -s . -p 'test_*.py' -v
python backtest.py sample_signals.csv --balance 10000 --risk 0.005
```

## Envio manual MT5 — risco real
O script exige BUY/SELL explícito, volume, SL, TP, sessão MT5 ligada, negociação permitida, spread limitado, sem posição existente no símbolo, volume válido, verificação `order_check` e confirmação digitada por ordem. Faz apenas uma submissão, sem retry automático. IA/YOLO **não** chamam o módulo.

**Começa em demo XM; o envio não foi verificado no terminal XM. Conta real está bloqueada por padrão**, mas existe opt-in explícito `NEXUS_ENABLE_LIVE_TRADING=I_ACCEPT_REAL_MONEY_RISK` e confirmação escrita separada por ordem. Teto no código: 0,50% da equity por ordem; padrão 0,25%. Essas travas não garantem segurança, preço, execução, nem resultado. Nunca testar a conta real nesta fase.

Backtests não incluem todos os custos e não provam vantagem. Não colocar senhas ou tokens no repositório.
