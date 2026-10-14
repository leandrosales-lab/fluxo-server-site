# Fluxo Server — copy da landing (portfólio)

> Vitrine técnica. Sem venda, sem promessa de resultado, sem link de instalação (repositório privado).
> Placeholder de contato: {{CONTATO}}

---

## Barra de navegação

- Fluxo Server
- Como funciona · Padrões · Fontes de dados · Replay · Engenharia · Status · FAQ
- Botão: Falar comigo → {{CONTATO}}

---

## Hero

**Selo:** Projeto de estudo · em desenvolvimento

**Título:**
Leitura de fluxo da B3, negócio a negócio.

**Subtítulo:**
Um motor em Python que recebe cada negócio do Times & Trades, identifica iceberg, absorção e exaustão, e explica cada sinal com os números que o geraram.

**Botões:**
- Ver como funciona → #como-funciona
- Falar comigo → {{CONTATO}}

**Terminal simulado** (rótulo acima: `exemplo ilustrativo — dados fictícios`):

```
$ python main.py --asset PETR4 --modo replay --arquivo pregao.csv
[INFO] Replay: 41.208 ticks de pregao.csv (0 linhas ignoradas)
[INFO] Iceberg CONFIRMADO (passiva): ITAU compra @ 37.42 | 9 execuções | vol 48.300 (4.2x lote médio) | fatia 71%
[REPLAY] BUY Iceberg @ 37.43 stop 37.40 conf 0.78
[INFO] Exaustão COMPRADORA (topo) @ 37.61 | vol 41% da média de 3 pernas | divergência de delta
[REPLAY] SELL Exaustão @ 37.58 stop 37.63 conf 0.71
[STATUS] PETR4 | Ticks: 5000 | Fluxo: 38.2%C 61.8%V | Delta 30s: -12.400
[INFO] Iceberg ROMPIDO: ITAU @ 37.42 (11 renovações, 61.900 vol total)
```

**Linha abaixo do terminal:**
Cada sinal sai com motivo, preço, stop e confiança. Nada de caixa-preta.

---

## Como funciona  (`#como-funciona`)

**Título:** Do negócio ao sinal, em quatro passos.

1. **Captura.** Cada negócio chega com preço, quantidade, lado agressor e as duas corretoras (quem agrediu e quem estava apregoado).
2. **Motor de fluxo.** O engine atualiza janelas de volume, delta, níveis de preço e pernas de movimento, sempre no horário do negócio, nunca no relógio do computador.
3. **Detectores.** Iceberg, absorção, exaustão, urgência e best offer rodam em paralelo e propõem candidatos de compra ou venda, cada um com sua confiança.
4. **Sinal.** O candidato mais forte acima da confiança mínima vira BUY ou SELL, com stop atrás do nível que o justificou. Abaixo disso, o motor fica em WAIT e diz por quê.

---

## Padrões detectados  (`#padroes`)

**Título:** O que o motor procura no Times & Trades.

**Iceberg pela corretora passiva**
- *Para o trader:* um player segurando um preço com ordem escondida, que se renova a cada vez que é agredida.
- *Como detecta:* a mesma corretora passiva executada várias vezes no mesmo preço, com volume bem acima do lote médio, por tempo mínimo, sem o preço atravessar o nível.

**Absorção**
- *Para o trader:* muita agressão num nível e o preço não passa.
- *Como detecta:* nível tocado várias vezes na janela, com volume agredido pelo menos 1,5x a média dos outros níveis; informa qual lado foi absorvido.

**Exaustão**
- *Para o trader:* o movimento faz nova máxima (ou mínima), mas cada vez com menos agressão.
- *Como detecta:* divide o preço em pernas (zigzag) e compara o volume a favor da última perna com a média das anteriores; divergência de delta, queda de velocidade e de lote médio somam confiança.

**Delta acumulado**
- *Para o trader:* quem está agredindo mais, comprador ou vendedor, no dia e nos últimos segundos.
- *Como detecta:* soma o volume agredido na compra menos o da venda, desde a abertura e numa janela curta configurável.

**Urgência**
- *Para o trader:* um player subindo (ou descendo) a escada de preços para conseguir executar.
- *Como detecta:* a mesma corretora agredindo em vários preços diferentes em poucos segundos.

**Best offer passivo**
- *Para o trader:* um player que fica sempre no primeiro nível do book.
- *Como detecta:* conta quantas vezes cada corretora aparece no melhor bid ou ask dentro de uma janela de tempo.

---

## Fontes de dados  (`#fontes`)

**Título:** Várias entradas, um formato de negócio.

| Fonte | O que entrega | Situação |
|---|---|---|
| **ProfitDLL (Nelogica)** | Cada negócio por callback, com lado agressor, as duas corretoras e o horário exato. Topo do book. Histórico de dias passados. | Implementada. Ainda não testada com a DLL real. |
| **RTD via Excel** | Um retrato do ativo a cada atualização. O servidor deduz quantidade, lado agressor e corretoras. | Implementada. Negócios que acontecem entre duas leituras chegam juntos, como um só. |
| **DDE e OCR** | Leitura por planilha ou pela tela. | Legado. Frágeis, mantidos só para testes. |
| **Replay de CSV** | Pregão gravado ou exportado do Times & Trades. | Testado com dados de exemplo. |

**Nota abaixo da tabela:**
A ProfitDLL é a fonte certa para fluxo: não perde negócio e já informa quem agrediu. As outras existem porque nem sempre a DLL está disponível.

---

## Replay e calibração  (`#replay`)

**Título:** O mesmo pregão, os mesmos sinais. Sempre.

- **Determinístico.** O motor usa o horário de cada negócio como relógio. Um pregão gravado produz exatamente os mesmos sinais em qualquer velocidade, ao vivo ou acelerado.
- **Gravação.** Qualquer modo ao vivo grava os negócios num CSV (`--gravar`), pronto para reprocessar depois.
- **Mini backtest.** Para cada sinal, mede se o preço andou o alvo a favor antes de tocar o stop, dentro de um horizonte de tempo. Também registra o máximo a favor e o máximo contra (MFE e MAE).
- **Grid de parâmetros.** Roda o mesmo pregão para cada combinação de parâmetros (`--grid exhaustion_vol_ratio=0.5,0.6 ...`) e ordena o resultado numa tabela.

```
$ python main.py --asset PETR4 --modo replay --arquivo pregao.csv \
    --grid exhaustion_vol_ratio=0.5,0.6 exhaustion_reversal_ticks=2,3
```

**Linha final:**
O grid serve para calibrar por ativo, não para garantir resultado. Parâmetro ajustado demais a um único dia é ruído.

---

## Engenharia  (`#engenharia`)

**Título:** Pequeno, testável e sem dependências no núcleo.

- **Python puro.** O motor, a API e o replay usam só a biblioteca padrão. Dependências externas só nos modos de captura opcionais (OCR, DDE).
- **API HTTP embutida.** `GET /signal`, `GET /state` com delta, pernas, icebergs e absorções, `POST /tick` e `POST /rtd` para entrada de dados, e um dashboard que atualiza sozinho.
- **Integração com o Profit.** Um robô NTSL lê o sinal pela planilha; a ponte RTD é uma macro VBA que envia cada atualização ao servidor.
- **Thread-safe e sem bloquear a fonte.** Os callbacks da DLL só enfileiram; uma thread separada entrega os negócios ao motor na ordem de chegada.
- **20 grupos de teste**, cobrindo cada detector, a ponte da DLL com negócios simulados, a inferência do RTD, a API HTTP, a leitura de CSV do Profit, a gravação e o replay determinístico. Rodam em qualquer sistema, sem o Profit instalado.

**Stack em chips:** Python 3.10+ · biblioteca padrão · ctypes (ProfitDLL) · VBA (RTD) · NTSL · HTML/JS (dashboard)

---

## Status  (`#status`)

**Título:** Onde o projeto está, sem enfeite.

**Pronto e testado com dados de exemplo**
- Motor com iceberg pela passiva, absorção, exaustão, delta, urgência e best offer
- Replay determinístico, mini backtest e grid
- Ponte RTD com inferência de negócios
- API HTTP e dashboard

**Implementado, falta testar com o Profit real**
- ProfitDLL em tempo real e download de histórico
- Campos do RTD que dependem da versão do Profit

**Próximos passos**
1. **PETR4 com dados reais:** gravar e reprocessar pregões, primeira calibração.
2. **Mini índice (WIN):** calibração própria, outro tamanho de tick e outra liquidez.

**Linha final:**
Nenhum resultado foi medido com dados reais ainda. Quando houver, ele aparece aqui, com o tamanho da amostra.

---

## FAQ  (`#faq`)

**Dá lucro?**
Não sei, e ninguém sabe ainda. O motor não foi validado com dados reais. Mesmo depois de validado, um resultado passado em poucos pregões não garante nada.

**É um robô que opera sozinho?**
Não. O motor gera sinais com motivo e stop. A decisão de operar não faz parte deste projeto.

**Posso usar ou comprar?**
Não. É um projeto pessoal de estudo, sem venda e com código fechado por enquanto.

**Por que corretora passiva e não só o lote repetido?**
O lote aparente engana: algoritmos repetem lotes o tempo todo. Ver a mesma corretora sendo agredida no mesmo preço, com volume acima do normal, é um sinal mais limpo de ordem escondida. Sem a passiva, o motor ainda usa a regra do lote repetido, marcada como heurística fraca.

**Funciona com qualquer ativo?**
O motor sim; os parâmetros não. Tamanho do tick, lote médio e liquidez mudam muito entre uma ação e um contrato futuro. Cada ativo precisa da própria calibração.

**Precisa do Profit?**
Para dados ao vivo, sim, na mesma máquina. Para estudar, o replay roda com qualquer CSV de negócios.

---

## CTA final

**Título:** Quer conversar sobre fluxo ou sobre o projeto?
**Texto:** Dúvidas técnicas, ideias de detector ou propostas de trabalho em engenharia de dados de mercado.
**Botão:** Falar comigo → {{CONTATO}}

---

## Rodapé

**Aviso (fixo, sempre visível no rodapé):**
Projeto de estudo. Não é recomendação de investimento, oferta de produto ou serviço. Operar na bolsa envolve risco de perda. Os exemplos desta página usam dados fictícios.

**Linha final:** Fluxo Server · {{CONTATO}}
