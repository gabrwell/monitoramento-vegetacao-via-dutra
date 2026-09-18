"""Analisa o dataset Sentinel-2 e gera rótulos, figuras, mapa e resumo."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import folium
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache" / "matplotlib"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config/projeto_satelite.json")
    parser.add_argument("--entrada", default="data/processed/observacoes_sentinel.csv")
    parser.add_argument("--saida", default="data/processed/segmentos_priorizados.csv")
    return parser.parse_args()


def rotular(linha: pd.Series, config: dict) -> str:
    p90 = linha["ndvi_p90_atual"]
    delta = linha["delta_ndvi_media"]
    if p90 >= config["prioridade_alta_ndvi_p90"] or delta >= config["prioridade_alta_delta_ndvi"]:
        return "alta"
    if p90 >= config["prioridade_media_ndvi_p90"] or delta >= config["prioridade_media_delta_ndvi"]:
        return "media"
    return "baixa"


def main() -> int:
    args = argumentos()
    config = json.loads((ROOT / args.config).read_text(encoding="utf-8"))
    dados = pd.read_csv(ROOT / args.entrada)
    periodos = [periodo["nome"] for periodo in config["periodos"]]
    if len(periodos) != 2:
        raise ValueError("A análise comparativa requer exatamente dois períodos.")
    anterior, atual = periodos

    metricas = [
        "ndvi_media",
        "ndvi_mediana",
        "ndvi_p90",
        "fracao_vegetacao_densa",
        "fracao_valida",
        "pixels_validos",
    ]
    indice = ["ponto_id", "longitude", "latitude"]
    largo = dados.pivot_table(index=indice, columns="periodo", values=metricas, aggfunc="first")
    largo.columns = [f"{metrica}_{periodo}" for metrica, periodo in largo.columns]
    largo = largo.reset_index()
    for metrica in metricas:
        largo = largo.rename(
            columns={
                f"{metrica}_{anterior}": f"{metrica}_anterior",
                f"{metrica}_{atual}": f"{metrica}_atual",
            }
        )

    largo["delta_ndvi_media"] = largo["ndvi_media_atual"] - largo["ndvi_media_anterior"]
    largo["delta_fracao_densa"] = (
        largo["fracao_vegetacao_densa_atual"] - largo["fracao_vegetacao_densa_anterior"]
    )
    presenca_normalizada = np.clip((largo["ndvi_p90_atual"] - 0.10) / 0.40, 0, 1)
    crescimento_normalizado = np.clip(
        (largo["delta_ndvi_media"] + 0.05) / 0.15,
        0,
        1,
    )
    largo["indice_prioridade_0_100"] = (
        70 * presenca_normalizada + 30 * crescimento_normalizado
    ).round(1)
    largo["prioridade_inspecao"] = largo.apply(rotular, axis=1, config=config)
    largo["criterio_rotulo"] = largo.apply(
        lambda r: (
            f"ndvi_p90_atual={r['ndvi_p90_atual']:.3f}; "
            f"delta_ndvi={r['delta_ndvi_media']:.3f}"
        ),
        axis=1,
    )
    largo = largo.sort_values(["indice_prioridade_0_100", "ponto_id"], ascending=[False, True])

    destino = ROOT / args.saida
    destino.parent.mkdir(parents=True, exist_ok=True)
    largo.to_csv(destino, index=False, encoding="utf-8-sig")

    figuras = ROOT / "outputs/figures"
    figuras.mkdir(parents=True, exist_ok=True)
    ordem = ["baixa", "media", "alta"]
    cores = {"baixa": "#2ca25f", "media": "#fec44f", "alta": "#de2d26"}
    contagem = largo["prioridade_inspecao"].value_counts().reindex(ordem, fill_value=0)
    ax = contagem.plot.bar(color=[cores[v] for v in ordem], rot=0)
    ax.set_title("Pontos por prioridade de inspeção")
    ax.set_xlabel("Prioridade")
    ax.set_ylabel("Quantidade de pontos")
    ax.bar_label(ax.containers[0], padding=3)
    plt.tight_layout()
    plt.savefig(figuras / "distribuicao_prioridade.png", dpi=180)
    plt.close()

    plt.scatter(largo["ndvi_media_anterior"], largo["ndvi_media_atual"], alpha=0.7, s=24)
    limites = [
        float(min(largo["ndvi_media_anterior"].min(), largo["ndvi_media_atual"].min())),
        float(max(largo["ndvi_media_anterior"].max(), largo["ndvi_media_atual"].max())),
    ]
    plt.plot(limites, limites, "--", color="gray", linewidth=1)
    plt.xlabel(f"NDVI médio {anterior}")
    plt.ylabel(f"NDVI médio {atual}")
    plt.title("Comparação temporal do NDVI por ponto")
    plt.tight_layout()
    plt.savefig(figuras / "comparacao_ndvi.png", dpi=180)
    plt.close()

    largo["delta_ndvi_media"].plot.hist(bins=16, color="#3182bd", edgecolor="white")
    plt.axvline(0, color="black", linewidth=1)
    plt.xlabel(f"Variação do NDVI médio ({atual} − {anterior})")
    plt.ylabel("Quantidade de pontos")
    plt.title("Distribuição da variação temporal")
    plt.tight_layout()
    plt.savefig(figuras / "variacao_ndvi.png", dpi=180)
    plt.close()

    centro = [float(largo["latitude"].mean()), float(largo["longitude"].mean())]
    mapa = folium.Map(location=centro, zoom_start=12, tiles="OpenStreetMap")
    for linha in largo.itertuples():
        folium.CircleMarker(
            [linha.latitude, linha.longitude],
            radius=5,
            color=cores[linha.prioridade_inspecao],
            fill=True,
            fill_opacity=0.85,
            tooltip=f"{linha.ponto_id}: {linha.prioridade_inspecao}",
            popup=(
                f"<b>{linha.ponto_id}</b><br>Prioridade: {linha.prioridade_inspecao}<br>"
                f"NDVI atual: {linha.ndvi_media_atual:.3f}<br>"
                f"Variação: {linha.delta_ndvi_media:.3f}<br>"
                f"Vegetação densa: {linha.fracao_vegetacao_densa_atual:.1%}"
            ),
        ).add_to(mapa)
    mapa.save(ROOT / "outputs/mapa_prioridades.html")

    resumo = {
        "fonte": config["fonte"],
        "pontos_planejados": int(len(pd.read_csv(ROOT / "data/raw/pontos_amostragem.csv"))),
        "pontos_comparaveis": int(len(largo)),
        "observacoes_reais": int(len(dados)),
        "periodos": periodos,
        "prioridades": {chave: int(valor) for chave, valor in contagem.items()},
        "ndvi_medio_anterior": float(largo["ndvi_media_anterior"].mean()),
        "ndvi_medio_atual": float(largo["ndvi_media_atual"].mean()),
        "delta_ndvi_medio": float(largo["delta_ndvi_media"].mean()),
        "delta_ndvi_mediano": float(largo["delta_ndvi_media"].median()),
        "fracao_valida_media_anterior": float(largo["fracao_valida_anterior"].mean()),
        "fracao_valida_media_atual": float(largo["fracao_valida_atual"].mean()),
        "regra_rotulo": {
            "alta": (
                f"NDVI p90 atual >= {config['prioridade_alta_ndvi_p90']} "
                f"ou delta NDVI >= {config['prioridade_alta_delta_ndvi']}"
            ),
            "media": (
                f"NDVI p90 atual >= {config['prioridade_media_ndvi_p90']} "
                f"ou delta NDVI >= {config['prioridade_media_delta_ndvi']}"
            ),
            "baixa": "demais pontos",
        },
    }
    (ROOT / "outputs/resumo_resultados.json").write_text(
        json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
    print(f"Base priorizada salva em {destino.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
