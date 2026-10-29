# Referências avaliadas

Os URLs enviados eram tópicos GitHub, não repositórios. Revisão inicial em 29-10-2026; não copiámos nem executámos fontes externas.

## Adequados como estudo ou futuro adaptador

- [aiomql](https://github.com/Ichinga-Samuel/aiomql) — framework async Python para MT5, MIT, Windows/terminal MT5, último push consultado 26-07-2026. Tem execução de ordens; apenas referência para arquitetura, não integrar antes de auditar.
- [ICT_Library_MQ5](https://github.com/xxvw/ICT_Library_MQ5) — biblioteca de padrões ICT para MQL5, MIT, atividade em outubro de 2026. Pode inspirar detecção de padrões, não demonstra desempenho.
- [jordantete/grid_trading_bot](https://github.com/jordantete/grid_trading_bot) — grid de cripto, backtest/paper/Grafana, MIT, ativo. Nosso `GridResearch` apenas produz níveis de pesquisa: nada de ordens. Grid não é automaticamente adequado a forex e pode acumular perdas em tendências.
- [hummingbot/dashboard](https://github.com/hummingbot/dashboard) — dashboard Hummingbot/cripto, Apache-2.0; arquitetura maior com Docker, não encaixa como dependência no bot MT5.
- [BetterTradingAgents](https://github.com/kingabzpro/BetterTradingAgents) — estudo de agentes e paper trading, MIT conforme dados públicos, orientado a ações e fornecedores externos de dados/LLM. A atividade/claims são dos autores; não prova vantagem.
- [OpenAlgo](https://github.com/marketcalls/openalgo) — plataforma extensa com conectores e opções, AGPL-3.0. Não copiar sem revisão das obrigações da licença nem assumir suporte ao broker/mercado do Nexus.
- [lambdaclass/options_portfolio_backtester](https://github.com/lambdaclass/options_portfolio_backtester) — pesquisa/backtest de opções, MIT conforme metadados. Pesquisa separada, não motor de forex MT5.
- [goldspanlabs/optopsy](https://github.com/goldspanlabs/optopsy) — análise de opções, AGPL-3.0; não integrar sem necessidade e revisão de licença.
- [kernc/backtesting.py](https://github.com/kernc/backtesting.py) — framework backtest, AGPL-3.0; manter como referência por enquanto.

A licença de um repositório não cobre automaticamente dependências; confirme o LICENSE e as obrigações antes de incorporar. Popularidade e descrições não comprovam segurança ou rentabilidade.

## Arquitetura do Nexus

- Núcleo MT5/forex em Windows; Android pode ser cliente de visualização/alertas mais tarde, não hospeda diretamente o terminal MetaTrader 5 para desktop.
- Grid e opções permanecem módulos de pesquisa, sem encaminhar sinais ao mercado.
- IA é uma interface de revisão explicável; o adaptador atual é local e determinístico, sem chamadas de rede ou poder de executar operações.
- Monitorização grava eventos JSONL localmente; não guardar passwords, tokens ou IDs privados.
- A versão atual só analisa/backtesta. Sem funções de envio de ordens.


## IA local

O Nexus tem um cliente opcional para a API local do [Ollama](https://docs.ollama.com/api/introduction). O modelo apenas comenta dados resumidos; regras determinísticas continuam responsáveis pelos filtros. A chamada usa localhost, formato JSON e falha fechada. Não colocamos credenciais nem endpoint de trading. O teste automatizado usa um transporte simulado; ainda não foi testado contra um modelo instalado.
