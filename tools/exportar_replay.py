"""
Roda o motor do Fluxo Server sobre um CSV de negócios e exporta a evolução do
estado (um quadro por negócio) para o mini-dashboard animado da landing.

Uso:
    python tools/exportar_replay.py <pasta do fluxo-server-profit> [csv] [saida]

Padrão: o CSV de exemplo do próprio projeto (replay/exemplo_wdo.csv, mini dólar,
tick 0,5) e img/replay.json. Os números do JSON são os que o motor real calculou.
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
    csv_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(raiz, "replay", "exemplo_wdo.csv")
    saida = sys.argv[3] if len(sys.argv) > 3 else os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "img", "replay.json")

    sys.path.insert(0, raiz)
    logging.disable(logging.CRITICAL)
    from core.engine import FlowEngine, EngineConfig, Side
    from config.conhecimento_videos import aplicar_conhecimento
    from replay.csv_ticks import ler_csv

    # Mesma configuração do main.py no replay do exemplo (--tick-size 0.5)
    engine = FlowEngine("WDOFUT", EngineConfig(tick_size=0.5))
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
        "ativo": "WDOFUT",
        "inicio": datetime.datetime.fromtimestamp(t0).strftime("%H:%M:%S"),
        "aviso": "Replay do CSV de exemplo do projeto. Dados de exemplo, não de um pregão real.",
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
