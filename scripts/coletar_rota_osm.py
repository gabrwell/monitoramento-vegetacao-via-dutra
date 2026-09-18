"""Obtém do OpenStreetMap a geometria auxiliar da BR-116 no recorte."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from verde_rodovias.geometria import validar_bbox  # noqa: E402

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config/projeto.json")
    parser.add_argument("--saida", default=None)
    return parser.parse_args()


def main() -> int:
    args = argumentos()
    config_path = ROOT / args.config
    config = json.loads(config_path.read_text(encoding="utf-8"))
    min_lon, min_lat, max_lon, max_lat = validar_bbox(config["bbox"])
    saida = ROOT / (args.saida or config["rota_geojson"])

    # Overpass usa sul,oeste,norte,leste.
    bbox_overpass = f"{min_lat},{min_lon},{max_lat},{max_lon}"
    consulta = f"""
    [out:json][timeout:60];
    (
      way["highway"]["ref"~"BR[- ]?116|SP[- ]?060",i]({bbox_overpass});
      way["highway"]["name"~"Dutra",i]({bbox_overpass});
    );
    out tags geom;
    """
    dados = urllib.parse.urlencode({"data": consulta}).encode("utf-8")
    requisicao = urllib.request.Request(
        OVERPASS_URL,
        data=dados,
        headers={"User-Agent": "verde-rodovias-academico/0.1"},
    )
    try:
        with urllib.request.urlopen(requisicao, timeout=90) as resposta:
            resultado = json.load(resposta)
    except urllib.error.URLError as erro:
        print(f"Falha ao consultar o Overpass: {erro.reason}", file=sys.stderr)
        return 1

    features = []
    ids_vistos = set()
    for elemento in resultado.get("elements", []):
        osm_id = elemento.get("id")
        geometria = elemento.get("geometry") or []
        coordenadas = [[p["lon"], p["lat"]] for p in geometria if "lon" in p and "lat" in p]
        if osm_id in ids_vistos or len(coordenadas) < 2:
            continue
        ids_vistos.add(osm_id)
        tags = elemento.get("tags") or {}
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "osm_id": osm_id,
                    "name": tags.get("name", ""),
                    "ref": tags.get("ref", ""),
                    "highway": tags.get("highway", ""),
                    "source": "OpenStreetMap contributors",
                },
                "geometry": {"type": "LineString", "coordinates": coordenadas},
            }
        )

    if not features:
        print("A consulta não retornou segmentos rodoviários.", file=sys.stderr)
        return 2

    geojson = {
        "type": "FeatureCollection",
        "name": "BR-116 Via Dutra — recorte inicial",
        "attribution": "© OpenStreetMap contributors, ODbL",
        "features": features,
    }
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(json.dumps(geojson, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Rota salva em {saida.relative_to(ROOT)} ({len(features)} segmentos).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
