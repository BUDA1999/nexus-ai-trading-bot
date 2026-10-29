# Nexus AI Trading Bot

Protótipo modular de estudo para sinais visuais + contexto numérico MT5, filtros de risco, monitorização local e pesquisa de estratégias. **Não envia ordens. Não é aconselhamento financeiro.**

## Módulos

- `trading_bot/core.py`: EMA, ATR, filtro direcional, stop/alvo ATR e dimensionamento com limite de risco.
- `trading_bot/strategies.py`: interface de estratégias, filtro visão+tendência e níveis de grelha para pesquisa (não ordens).
- `trading_bot/ai_review.py`: contrato de revisão segura, atualmente sem IA externa nem execução.
- `trading_bot/monitoring.py`: auditoria local JSONL e resumo de resultados.
- `trading_bot/research/options.py`: preço teórico Black-Scholes para estudo europeu, sem corretora nem ordens.
- `trading_bot/adapters/mt5_readonly.py`: adaptador MT5 opcional, apenas leitura de candles fechados.
- `trading_bot/backtest.py`: backtest offline com sinais/tendências fornecidos num CSV.

## Plataforma

Começar localmente num **PC Windows**: a integração Python oficial do MT5 depende do terminal MetaTrader 5 desktop. O scanner visual também captura a tela. Android pode ser acrescentado depois como painel de consulta/alertas; não deve executar o terminal MT5 desktop nem guardar credenciais de trading.

## Testar

Python 3.10+ para núcleo; nenhum pacote externo para testes do núcleo.

```bash
python -m unittest discover -s tests -v
python -m trading_bot.backtest data/sample_signals.csv --balance 10000 --risk 0.005
```

A ligação MT5 é opcional e requer Windows, terminal aberto e pacote MetaTrader5 instalado; `read_closed_rates` é apenas leitura. Não há API de execução de ordens neste projeto.

## Limitações e plano seguro

Backtests podem omitir spread variável, slippage, comissões, swap, gaps, execução parcial e conversão de moedas. Os dados e resultados de exemplo não representam desempenho. Validar em histórico fora da amostra, comparar com baseline OHLC, testar conta demo e colocar limites de paragem antes de sequer considerar qualquer execução.

Análise das referências, licenças e razão de separar MT5, grid e opções em [REFERENCIAS.md](REFERENCIAS.md).


## Envio manual MT5 — avançado

O script `mt5_manual_execution.py` aceita apenas ordem market indicada pelo utilizador, com SL/TP obrigatórios, valida símbolo, spread, posição duplicada, volume e perda estimada pelo terminal. Faz `order_check` e envia uma vez, sem repetição automática. A IA e o detector visual não o chamam. Começa exclusivamente com a conta DEMO da XM.

Conta REAL fica bloqueada por padrão. O código exige opt-in `NEXUS_ENABLE_LIVE_TRADING=I_ACCEPT_REAL_MONEY_RISK` **e** confirmação exata escrita para cada operação; limite máximo por ordem no programa: 0,50% de equity (padrão 0,25%). Isso não torna uma estratégia segura nem constitui recomendação de negociação. O utilizador continua responsável por confirmar os detalhes e verificar o terminal. O módulo não foi testado contra broker real.
