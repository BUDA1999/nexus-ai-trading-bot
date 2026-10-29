# Nexus AI Trading Bot

Protótipo de estudo para explorar análise híbrida com inteligência artificial, visão computacional e contexto de mercado.

Protótipo educativo para testar a ideia de combinar sinais visuais com contexto de mercado. **Não envia ordens e não é aconselhamento financeiro.** Esta primeira versão está deliberadamente limitada a análise/backtest offline; não introduz execução real no MT5.

## O que já existe

- Indicadores puros em Python: EMA com aquecimento explícito e ATR de Wilder.
- Filtro de sinal: compras só com tendência UP, vendas só com DOWN; recusa tendência lateral, spread excessivo e dados inválidos.
- Stop e alvo derivados do ATR.
- Dimensionamento de posição arredondado para baixo, com teto de risco de 2% e limite de tamanho.
- Backtest de sinais rotulados em CSV. A decisão no fecho só pode entrar na abertura da vela seguinte. Se stop e alvo forem atingidos dentro da mesma vela, assume-se o stop primeiro (conservador).
- Testes automáticos para os cálculos principais.

## Diferença pretendida

Muitos bots tradicionais avaliam diretamente preços e indicadores. Este projeto quer investigar uma abordagem híbrida: o detector visual (YOLO) propõe BUY/SELL e o contexto numérico do MT5 pode filtrar a proposta. **A visão ainda não foi validada** e não é tratada como prova de vantagem. A comparação correta é testar, no mesmo período e com custos, (1) regras só com OHLC e (2) visão + filtros, incluindo uma estratégia de referência simples.

## Requisitos e teste

Python 3.10+; o núcleo não precisa de pacotes externos.

```bash
python -m unittest discover -s tests -v
python -m trading_bot.backtest data/sample_signals.csv --balance 10000 --risk 0.005
```

## Formato do CSV

`time,open,high,low,close,signal,trend,spread,atr`

- `signal`: BUY, SELL ou NONE. Para já, sinal e tendência são entradas previamente preparadas/rotuladas; o exemplo não é um resultado de mercado.
- `trend`: UP, DOWN ou FLAT, calculada apenas com velas fechadas do timeframe macro.
- `spread` e `atr`: valores em unidades de preço, não points/pips; confirme as unidades do símbolo e do broker.
- Linhas em ordem cronológica. Dados devem ser limpos, sem candles futuros nem look-ahead.

## Limitações importantes

- O backtest é um instrumento de estudo, não uma previsão nem garantia de desempenho. Não simula slippage, swap, comissões, gaps, execução parcial ou conversão cambial da conta.
- `contract_size` depende do ativo e da moeda da conta; não use o valor padrão como se fosse válido para qualquer símbolo.
- Um modelo treinado em imagens pode falhar com tema, zoom, escala, broker e timeframe diferentes. Guardar screenshot, confiança, versão do modelo e resultado futuro é necessário antes de tirar conclusões.
- Não ligue uma conta real nem acrescente envio de ordens antes de validar dados, regras, risco e o comportamento numa conta demo. A versão atual não possui qualquer função de envio de ordens.

## Próximos passos de investigação

1. Importar histórico M5/H1 de um único símbolo e documentar zona horária, spread e custos.
2. Criar dataset de imagens rotuladas por pessoa e separar períodos de treino, validação e teste por data.
3. Comparar resultados fora da amostra: taxa de acerto, retorno líquido, drawdown máximo, expectativa por operação e número de sinais.
4. Testar walk-forward, custos realistas, estabilidade em outros períodos e um baseline sem YOLO.
5. Só depois considerar paper trading em tempo real, ainda sem dinheiro real.

## Segurança

Não coloque passwords, tokens, dados de conta ou ficheiros `.env` no GitHub. Este repositório não precisa de credenciais para executar testes.
