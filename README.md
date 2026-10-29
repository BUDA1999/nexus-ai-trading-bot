# Nexus AI Trading Bot

Protótipo modular educativo com sinais, filtros de risco, IA consultiva local e ferramentas de pesquisa para MT5. Inclui envio manual com salvaguardas; **não é aconselhamento financeiro e não garante lucro nem segurança**.

## Execução manual MT5
`mt5_manual_execution.py` aceita uma ordem market introduzida pelo utilizador, com BUY/SELL, volume, stop-loss e take-profit obrigatórios. Verifica terminal ligado, negociação permitida, símbolo, spread, distância mínima SL/TP, posição duplicada, volume, perda estimada pelo MT5, modo de preenchimento e `order_check`. Submete uma só vez e não repete automaticamente se a resposta ficar incerta. IA e YOLO nunca chamam este módulo.

**Começar apenas numa conta DEMO XM/MT5 num PC Windows.** A integração não foi testada no terminal XM. A conta REAL está bloqueada por padrão; o desbloqueio exige opt-in `NEXUS_ENABLE_LIVE_TRADING=I_ACCEPT_REAL_MONEY_RISK` e confirmação textual exata para cada ordem. Limite de risco do código: máximo 0,50% da equity por ordem (padrão 0,25%). Estes limites não garantem segurança ou execução correta. Não testar com dinheiro real.

## IA
`ai_ollama.py` usa Ollama local para comentar um sinal resumido. Não escolhe lotes, não altera stops e não envia ordens. Se não responder, fica indisponível. Não enviar credenciais ao modelo.

## Pesquisa
- `core.py`: EMA, ATR, filtros e dimensionamento.
- `backtest.py`: backtest offline em CSV.
- `strategies.py`: filtro de tendência e níveis GRID só para estudo.
- `monitoring.py`: registo JSONL local.
- `options_research.py`: Black–Scholes demonstrativo.
- `mt5_readonly.py`: leitura opcional de velas fechadas.
- `REFERENCIAS.md`: fontes avaliadas e licenças.

Grid e opções não estão conectados a ordens. O CSV de exemplo é artificial e não prova desempenho.

## Testar
Python 3.10+; testes usam mocks e não conectam ao broker:

```bash
python -m unittest discover -s . -p 'test_*.py' -v
python backtest.py sample_signals.csv --balance 10000 --risk 0.005
```

MT5 Python requer terminal de desktop em Windows; Android pode servir como painel de consulta/alertas, não como terminal MT5. Backtests não incluem necessariamente todos os custos e não garantem resultados. Mantenha passwords e tokens fora do GitHub.
