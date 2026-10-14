# Recon — estrutura da landing habblaud.com (referência para o Fluxo Server)

Escopo: só a **estrutura** da landing pública (web, desktop 1440px e mobile 390px), como referência de ritmo
e componentes para a landing de portfólio do Fluxo Server. Nenhum texto, imagem, marca ou código do original
entra no site. Capturado em 2026-10-14, uma visita, sem login.

## Fontes

| fonte | URL |
| --- | --- |
| landing (marketing site) | https://habblaud.com/ |
| repositório público (README, para entender o produto) | https://github.com/marmottajr/habblaud |

Screenshots de referência (nunca vão para o site): `replica/screens/habblaud-desktop.png`, `habblaud-mobile.png`.

## Inventário de seções (a "tela" aqui é uma página longa)

Altura total ~25.600px no desktop. 18 blocos.

| ID | bloco | âncora | y (px) | função | componentes |
| --- | --- | --- | --- | --- | --- |
| S01 | Header fixo | — | 0 | navegação + CTA | logo, 4 links âncora, seletor de idioma, botão secundário (estrela GitHub), botão primário |
| S02 | Hero | #top | 0–1900 | promessa + prova visual | selo de versão, H1, subtítulo, 2 CTAs, bloco de comando copiável, screenshot grande |
| S03 | Compatibilidade | #agentes | 1927 | "funciona com X e Y" | cards lado a lado, tabela comparativa |
| S04 | Instalação | #instalar | 3038 | como começar | abas (2 modos), lista de SOs, 4 passos numerados |
| S05 | Antes/depois | — | 6314 | problema → solução | 2 colunas contrastantes com imagens |
| S06 | Como funciona | #como-funciona | 9014 | fluxo passo a passo | terminal simulado, linha do tempo |
| S07 | Destaque 1 | — | 12225 | painel de status | screenshot + texto |
| S08 | Destaque 2 | — | 13315 | ver o trabalho | screenshot + texto |
| S09 | Destaque 3 | #responder | 14605 | ação remota | mockup de celular |
| S10 | Grade de recursos | #recursos | 15533 | lista de capacidades | grid de cards com ícone |
| S11 | Destaque 4 | — | 17943 | comportamento automático | animação/screenshot |
| S12 | Destaque 5 (lazer) | — | 21003 | personalidade | imagens animadas |
| S13 | Casos de uso | #casos | 21908 | para quem é | cards de persona |
| S14 | Privacidade | — | 22760 | confiança | trecho de terminal com dados mascarados |
| S15 | FAQ | #faq | 23953 | objeções | acordeão |
| S16 | CTA final | #comecar | 24876 | conversão | H2 + botões |
| S17 | Rodapé | — | 25641 | links + licença | colunas de links, copyright |

Estados: mobile empilha tudo em uma coluna; header vira menu compacto. No dia da captura, parte dos textos
aparecia como placeholder de template (bug de tradução do original — não replicar).

## Fluxos

F01 Visitante entende e vai agir: S01/S02 (CTA) → S04 instalar. 1 clique no CTA do hero.
F02 Visitante cético: S02 → S05 antes/depois → S14 privacidade → S15 FAQ → S16 CTA.
Para o Fluxo Server (portfólio, sem instalação pública) o CTA vira "contato / ver no GitHub".

## Componentes recorrentes

Botão primário/secundário · selo (badge) · bloco de comando/terminal simulado · card com ícone · abas ·
lista numerada de passos · tabela comparativa · antes/depois em 2 colunas · acordeão FAQ · header fixo com
âncoras · rodapé em colunas.

## Mapeamento para o Fluxo Server (design já feito no Stitch)

| original | Fluxo Server |
| --- | --- |
| S02 hero + screenshot | hero + terminal de sinais (exemplo fictício) |
| S03 compatibilidade | faixa de números (detectores, fontes, replay, testes) |
| S04 instalação (abas) | fontes de dados (abas: DLL, RTD, Replay CSV, Manual) |
| S05 antes/depois | antes/depois: T&T bruto → sinal estruturado |
| S06 como funciona | pipeline negócio → engine → sinal |
| S10 grade de recursos | grade dos 6 padrões |
| S07–S09, S11 destaques | replay e calibração (relatório) + engenharia |
| S13 casos de uso | (fora — portfólio) |
| S14 privacidade | aviso de risco / status honesto |
| S15 FAQ / S16 CTA / S17 rodapé | FAQ / contato / rodapé com aviso |

## Fora do escopo (não clonável ou não aplicável)

Marca, nome, pixel art, screenshots e textos do original; seletor de 4 idiomas; mockup de celular/aprovação
remota; seções de personalidade (lounge); botão de instalação (o repo do Fluxo Server é privado).

## Tamanho

S — uma página estática, ~13 blocos, sem backend. Partes mais difíceis: terminal animado acessível,
abas sem framework, responsividade das tabelas largas no mobile.
