"""
Gera um pregão SINTÉTICO da PETR4 (dados inventados, determinísticos) no formato
de CSV do replay do Fluxo Server, para a animação da landing. Não é um pregão real.

Roteiro (~8 min), pensado para exercitar os detectores com parâmetros de ação
(tick R$ 0,01, lotes de 100):
  1. acumulação em 37,40 com a mesma corretora passiva segurando a venda (iceberg comprador)
  2. alta em três pernas, cada uma com menos agressão (exaustão no topo)
  3. queda com um player vendendo em vários preços em poucos segundos (urgência)
  4. agressão vendedora travada num nível (absorção) e repique

Uso: python tools/gerar_exemplo_petr4.py [saida.csv]
"""

import csv
import os
import random
import sys
from datetime import datetime

random.seed(20261014)

CORRETORAS = ["XP INC", "BTG PACTUAL", "ITAU", "BRADESCO", "SANTANDER", "UBS", "SAFRA",
              "GENIAL", "CLEAR", "MORGAN STANLEY", "JP MORGAN", "TORO", "INTER", "RICO"]
INICIO = datetime(2026, 10, 13, 10, 15, 0).timestamp()

linhas = []
t = INICIO
preco = 37.40


def outro(*evitar):
    return random.choice([c for c in CORRETORAS if c not in evitar])


def neg(dt, p, qtd, lado, agressora=None, passiva=None):
    """Um negócio dt segundos depois do anterior. lado: B (compra agride) ou S (venda agride)."""
    global t, preco
    t += dt
    preco = round(p, 2)
    ag = agressora or outro()
    linhas.append([f"{t:.3f}", f"{preco:.2f}", qtd, lado, ag, passiva or outro(ag)])


def lote():
    return random.choice([100, 100, 100, 200, 200, 300, 500])


# 1. Acumulação: ITAU passivo comprando em 37,40; vendedores batem e o preço não cai
for i in range(26):
    if i % 3 == 2:
        neg(random.uniform(1.5, 3.0), 37.41, lote(), "B")
    else:
        neg(random.uniform(1.5, 3.5), 37.40, random.choice([200, 300, 500, 800]), "S", passiva="ITAU")

# 2. Alta em três pernas, cada uma com menos agressão compradora; recuos de 4 centavos
perna_topo = [37.48, 37.54, 37.58]
perna_lote = [[800, 1000, 1200], [400, 500, 600], [100, 200]]
inicio_perna = 37.41
for k, topo in enumerate(perna_topo):
    p = inicio_perna
    while p < topo - 1e-9:
        p = round(p + 0.01, 2)
        neg(random.uniform(0.6, 1.6), p, random.choice(perna_lote[k]), "B")
        if random.random() < 0.25:
            neg(random.uniform(0.6, 1.5), p, 100, "S")
    # recuo que fecha a perna (≥ 3 ticks)
    for d in (0.01, 0.02, 0.03, 0.04):
        neg(random.uniform(0.8, 1.8), topo - d, random.choice([100, 200]), "S")
    inicio_perna = round(topo - 0.04, 2)

# 3. Queda: BTG PACTUAL vendendo com urgência em vários preços seguidos
p = preco
for _ in range(7):
    p = round(p - 0.01, 2)
    neg(random.uniform(0.4, 1.2), p, random.choice([500, 800, 1000]), "S", agressora="BTG PACTUAL")
for _ in range(8):
    p = round(p - 0.01, 2)
    neg(random.uniform(0.8, 2.0), p, lote(), "S")
    if random.random() < 0.3:
        neg(random.uniform(0.6, 1.4), p + 0.01, 100, "B")

# 4. Absorção: muita venda batendo no mesmo preço sem passar; depois repique
nivel = round(preco - 0.01, 2)
for i in range(22):
    if i % 4 == 3:
        neg(random.uniform(1.0, 2.5), nivel + 0.01, lote(), "B")
    else:
        neg(random.uniform(1.0, 2.5), nivel, random.choice([500, 800, 1000, 1500]), "S")
p = nivel
for _ in range(9):
    p = round(p + 0.01, 2)
    neg(random.uniform(0.7, 1.6), p, random.choice([300, 500, 800]), "B")
    if random.random() < 0.3:
        neg(random.uniform(0.6, 1.4), p, 100, "S")
for _ in range(10):
    neg(random.uniform(1.5, 3.0), p + random.choice([-0.01, 0, 0.01]), lote(), random.choice("BS"))

saida = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dados", "exemplo_petr4_sintetico.csv")
os.makedirs(os.path.dirname(saida), exist_ok=True)
with open(saida, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["timestamp", "preco", "quantidade", "agressor", "corretora_agressora", "corretora_passiva"])
    w.writerows(linhas)
print(f"{len(linhas)} negócios sintéticos, {(t - INICIO) / 60:.1f} min -> {saida}")
