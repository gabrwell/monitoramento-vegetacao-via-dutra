"""Constrói o dataset real de NDVI Sentinel-2 ao longo da BR-116."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from verde_rodovias.satelite import (  # noqa: E402
    carregar_recorte_item,
    consultar_itens,
    gerar_pontos_rota,
    medir_pontos,
)


def argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config/projeto_satelite.json")
    parser.add_argument("--saida", default="data/processed/observacoes_sentinel.csv")
    return parser.parse_args()


def main() -> int:
    args = argumentos()
    config = json.loads((ROOT / args.config).read_text(encoding="utf-8"))
    pontos = gerar_pontos_rota(
        ROOT / config["rota_geojson"],
        distancia_minima_m=float(config["distancia_pontos_m"]),
        max_pontos=int(config["max_pontos"]),
    )
    if not pontos:
        print("Nenhum ponto foi gerado para a rodovia.", file=sys.stderr)
        return 2
    print(f"Pontos de amostragem: {len(pontos)}")
    pd.DataFrame(pontos).to_csv(ROOT / "data/raw/pontos_amostragem.csv", index=False, encoding="utf-8-sig")

    resultados = []
    auditoria_itens = []
    for periodo in config["periodos"]:
        print(f"Consultando período {periodo['nome']}...")
        itens = consultar_itens(
            config["bbox"],
            periodo["inicio"],
            periodo["fim"],
            float(config["cobertura_nuvens_max_pct"]),
        )
        if not itens:
            print(f"Nenhuma cena encontrada para {periodo['nome']}.", file=sys.stderr)
            return 3
        print(f"Cenas selecionadas: {len(itens)}")
        recortes = []
        for item in itens:
            auditoria_itens.append(
                {
                    "periodo": periodo["nome"],
                    "item_id": item.id,
                    "data": item.datetime.date().isoformat(),
                    "tile": item.properties.get("s2:mgrs_tile") or item.id.split("_")[5],
                    "nuvens_item_pct": item.properties.get("eo:cloud_cover"),
                }
            )
            print(f"Lendo {item.id}...")
            recorte = carregar_recorte_item(item, config["bbox"])
            if recorte:
                recortes.append(recorte)
        medidos = medir_pontos(
            pontos,
            recortes,
            raio_m=float(config["raio_analise_m"]),
            limite_vegetacao_densa=float(config["ndvi_vegetacao_densa"]),
        )
        for medicao in medidos:
            medicao["periodo"] = periodo["nome"]
        resultados.extend(medidos)
        print(f"Pontos válidos em {periodo['nome']}: {len(medidos)}")

    destino = ROOT / args.saida
    destino.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(resultados).to_csv(destino, index=False, encoding="utf-8-sig")
    (ROOT / "data/raw/itens_sentinel.json").write_text(
        json.dumps(auditoria_itens, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Dataset salvo em {destino.relative_to(ROOT)} com {len(resultados)} observações reais.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
