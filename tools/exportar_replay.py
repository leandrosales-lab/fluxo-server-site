"""
Roda o motor do Fluxo Server sobre um CSV de negócios e exporta a evolução do
estado (um quadro por negócio) para o mini-dashboard animado da landing.

Uso:
    python tools/exportar_replay.py <pasta do fluxo-server-profit> [csv] [saida] [ativo] [tick]

Padrão: dados/exemplo_petr4_sintetico.csv (gerado por tools/gerar_exemplo_petr4.py),
ativo PETR4, tick 0,01, saída img/replay.json. Os números do JSON são os que o motor
real calculou sobre esse CSV.
"""

import datetime
import json
import logging
import os
import sys


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    raiz = os.path.abspath(sys.argv[1])
    site = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(site, "dados", "exemplo_petr4_sintetico.csv")
    saida = sys.argv[3] if len(sys.argv) > 3 else os.path.join(site, "img", "replay.json")
    ativo = sys.argv[4] if len(sys.argv) > 4 else "PETR4"
    tick = float(sys.argv[5]) if len(sys.argv) > 5 else 0.01

    sys.path.insert(0, raiz)
    logging.disable(logging.CRITICAL)
    from core.engine import FlowEngine, EngineConfig, Side
    from config.conhecimento_videos import aplicar_conhecimento
    from replay.csv_ticks import ler_csv

    # Mesma configuração do main.py (EngineConfig + conhecimento aplicado)
    engine = FlowEngine(ativo, EngineConfig(tick_size=tick))
    aplicar_conhecimento(engine)

    ticks = ler_csv(csv_path).ticks
    t0 = ticks[0].timestamp
    quadros = []
    for t in ticks:
        engine.add_tick(t)
        st = engine.get_state()
        sig = st["signal"]
        q = {
            "t": round((t.timestamp - t0) * 1000),          # ms desde o 1º negócio
            "p": t.price, "q": t.qty,
            "s": "C" if t.side == Side.BUY else "V",
            "b": t.broker, "pb": t.passive_broker,
            "fb": st["flow_pct_buy"],
            "dc": st["delta"]["cumulative"], "dw": st["delta"]["window"],
            "sg": sig["signal"],
        }
        if sig["signal"] in ("BUY", "SELL"):
            q["sp"] = sig["pattern"]
            q["sc"] = sig["confidence"]
            q["px"] = sig["price"]
            q["st"] = sig["stop_price"]
        pad = []
        for e in st["exhaustions"][:1]:
            pad.append({"k": "Exaustão", "lado": "topo" if e["exhausted_side"] == "compra" else "fundo",
                        "px": e["extreme_price"]})
        for a in st["absorbed_levels"][:1]:
            pad.append({"k": "Absorção", "px": a["price"], "n": a["touches"]})
        for u in st["urgent_brokers"][:1]:
            pad.append({"k": "Urgência", "b": u["broker"], "lado": u["side"], "n": u["levels"]})
        for i in st["icebergs_confirmed"][:1]:
            pad.append({"k": "Iceberg", "b": i["broker"], "px": i["price"]})
        if pad:
            q["pt"] = pad
        quadros.append(q)

    dados = {
        "fonte": os.path.basename(csv_path),
        "ativo": ativo,
        "inicio": datetime.datetime.fromtimestamp(t0).strftime("%H:%M:%S"),
        "aviso": "Dados sintéticos de exemplo, não de um pregão real.",
        "quadros": quadros,
    }
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    with open(saida, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, separators=(",", ":"))
    sinais = sum(1 for a, b in zip([None] + quadros, quadros)
                 if b["sg"] in ("BUY", "SELL") and (a is None or a.get("sp") != b.get("sp") or a["sg"] != b["sg"]))
    print(f"{len(quadros)} quadros, {sinais} trocas de sinal, {os.path.getsize(saida):,} bytes -> {saida}")


if __name__ == "__main__":
    main()
