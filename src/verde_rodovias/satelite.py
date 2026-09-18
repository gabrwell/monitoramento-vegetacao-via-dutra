"""Aquisição e cálculo de métricas Sentinel-2 ao longo de uma rodovia."""

from __future__ import annotations

import json
import math
from contextlib import ExitStack
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
import planetary_computer as pc
import rasterio
from pyproj import Transformer
from pystac_client import Client
from rasterio.enums import Resampling
from rasterio.windows import Window, bounds as window_bounds, from_bounds

from .geometria import haversine_m

STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"
SCL_INVALIDAS = {0, 1, 3, 8, 9, 10, 11}


def gerar_pontos_rota(
    caminho_geojson: str | Path,
    distancia_minima_m: float = 150,
    max_pontos: int = 100,
) -> list[dict]:
    """Seleciona vértices espacialmente distribuídos das pistas principais."""
    objeto = json.loads(Path(caminho_geojson).read_text(encoding="utf-8"))
    candidatos: list[list[float]] = []
    for feature in objeto.get("features", []):
        propriedades = feature.get("properties") or {}
        geometria = feature.get("geometry") or {}
        if propriedades.get("highway") != "motorway":
            continue
        if geometria.get("type") == "LineString":
            candidatos.extend(geometria.get("coordinates") or [])

    selecionados: list[list[float]] = []
    for ponto in sorted(candidatos, key=lambda valor: (valor[0], valor[1])):
        if all(haversine_m(ponto, existente) >= distancia_minima_m for existente in selecionados):
            selecionados.append(ponto)

    if len(selecionados) > max_pontos:
        indices = np.linspace(0, len(selecionados) - 1, max_pontos).round().astype(int)
        selecionados = [selecionados[indice] for indice in sorted(set(indices))]

    return [
        {"ponto_id": f"P{indice:03d}", "longitude": float(p[0]), "latitude": float(p[1])}
        for indice, p in enumerate(selecionados, start=1)
    ]


def consultar_itens(
    bbox: Sequence[float], inicio: str, fim: str, nuvens_max_pct: float
) -> list:
    """Busca uma cena por tile MGRS, priorizando a menor cobertura de nuvens."""
    catalogo = Client.open(STAC_URL, modifier=pc.sign_inplace)
    busca = catalogo.search(
        collections=["sentinel-2-l2a"],
        bbox=list(bbox),
        datetime=f"{inicio}/{fim}",
        query={"eo:cloud_cover": {"lt": nuvens_max_pct}},
        max_items=100,
    )
    itens = list(busca.items())
    por_tile = {}
    for item in itens:
        tile = item.properties.get("s2:mgrs_tile") or item.id.split("_")[5]
        atual = por_tile.get(tile)
        nuvens = float(item.properties.get("eo:cloud_cover") or 100)
        if atual is None or nuvens < float(atual.properties.get("eo:cloud_cover") or 100):
            por_tile[tile] = item
    return sorted(por_tile.values(), key=lambda item: item.id)


def _janela_bbox(dataset, bbox: Sequence[float]) -> Window | None:
    transformer = Transformer.from_crs("EPSG:4326", dataset.crs, always_xy=True)
    min_lon, min_lat, max_lon, max_lat = bbox
    xs, ys = transformer.transform(
        [min_lon, min_lon, max_lon, max_lon],
        [min_lat, max_lat, min_lat, max_lat],
    )
    esquerda = max(min(xs), dataset.bounds.left)
    direita = min(max(xs), dataset.bounds.right)
    inferior = max(min(ys), dataset.bounds.bottom)
    superior = min(max(ys), dataset.bounds.top)
    if esquerda >= direita or inferior >= superior:
        return None
    janela = from_bounds(esquerda, inferior, direita, superior, dataset.transform)
    return janela.round_offsets().round_lengths().intersection(Window(0, 0, dataset.width, dataset.height))


def carregar_recorte_item(item, bbox: Sequence[float]) -> dict | None:
    """Lê B04, B08 e SCL apenas no recorte necessário."""
    opcoes_gdal = {
        "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
        "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".tif,.TIF",
    }
    with rasterio.Env(**opcoes_gdal), ExitStack() as pilha:
        vermelho_ds = pilha.enter_context(rasterio.open(item.assets["B04"].href))
        janela = _janela_bbox(vermelho_ds, bbox)
        if janela is None:
            return None
        vermelho = vermelho_ds.read(1, window=janela).astype("float32")
        transformacao = vermelho_ds.window_transform(janela)
        limite = window_bounds(janela, vermelho_ds.transform)
        crs = vermelho_ds.crs

        nir_ds = pilha.enter_context(rasterio.open(item.assets["B08"].href))
        nir = nir_ds.read(1, window=janela).astype("float32")

        scl_ds = pilha.enter_context(rasterio.open(item.assets["SCL"].href))
        janela_scl = from_bounds(*limite, transform=scl_ds.transform)
        scl = scl_ds.read(
            1,
            window=janela_scl,
            out_shape=vermelho.shape,
            resampling=Resampling.nearest,
            boundless=True,
            fill_value=0,
        )

    denominador = nir + vermelho
    ndvi = np.full(vermelho.shape, np.nan, dtype="float32")
    refletancia_valida = (vermelho > 0) & (nir > 0) & (denominador != 0)
    ndvi[refletancia_valida] = (nir[refletancia_valida] - vermelho[refletancia_valida]) / denominador[
        refletancia_valida
    ]
    mascara_scl = ~np.isin(scl, list(SCL_INVALIDAS))
    ndvi[~mascara_scl] = np.nan
    return {
        "item_id": item.id,
        "data_aquisicao": item.datetime.date().isoformat(),
        "tile": item.properties.get("s2:mgrs_tile") or item.id.split("_")[5],
        "nuvens_item_pct": float(item.properties.get("eo:cloud_cover") or 0),
        "ndvi": ndvi,
        "transform": transformacao,
        "crs": crs,
        "resolucao_m": abs(float(transformacao.a)),
    }


def medir_ponto(
    recorte: dict,
    longitude: float,
    latitude: float,
    raio_m: float,
    limite_vegetacao_densa: float,
) -> dict | None:
    """Calcula métricas de NDVI em uma vizinhança circular do ponto."""
    transformer = Transformer.from_crs("EPSG:4326", recorte["crs"], always_xy=True)
    x, y = transformer.transform(longitude, latitude)
    linha, coluna = rasterio.transform.rowcol(recorte["transform"], x, y)
    matriz = recorte["ndvi"]
    if linha < 0 or coluna < 0 or linha >= matriz.shape[0] or coluna >= matriz.shape[1]:
        return None

    raio_px = max(1, int(math.ceil(raio_m / recorte["resolucao_m"])))
    l0, l1 = max(0, linha - raio_px), min(matriz.shape[0], linha + raio_px + 1)
    c0, c1 = max(0, coluna - raio_px), min(matriz.shape[1], coluna + raio_px + 1)
    janela = matriz[l0:l1, c0:c1]
    linhas, colunas = np.ogrid[l0 - linha : l1 - linha, c0 - coluna : c1 - coluna]
    circular = linhas * linhas + colunas * colunas <= raio_px * raio_px
    valores = janela[circular]
    validos = valores[np.isfinite(valores)]
    if len(validos) < 10:
        return None
    return {
        "pixels_total": int(len(valores)),
        "pixels_validos": int(len(validos)),
        "fracao_valida": float(len(validos) / len(valores)),
        "ndvi_media": float(np.mean(validos)),
        "ndvi_mediana": float(np.median(validos)),
        "ndvi_p90": float(np.percentile(validos, 90)),
        "fracao_vegetacao_densa": float(np.mean(validos >= limite_vegetacao_densa)),
    }


def medir_pontos(
    pontos: Iterable[dict],
    recortes: Iterable[dict],
    raio_m: float,
    limite_vegetacao_densa: float,
) -> list[dict]:
    """Escolhe, em áreas de sobreposição, a medição com mais pixels válidos."""
    recortes = list(recortes)
    resultados = []
    for ponto in pontos:
        candidatos = []
        for recorte in recortes:
            medicao = medir_ponto(
                recorte,
                ponto["longitude"],
                ponto["latitude"],
                raio_m,
                limite_vegetacao_densa,
            )
            if medicao:
                candidatos.append({**ponto, **{k: v for k, v in recorte.items() if k not in {"ndvi", "transform", "crs"}}, **medicao})
        if candidatos:
            resultados.append(max(candidatos, key=lambda valor: (valor["pixels_validos"], valor["fracao_valida"])))
    return resultados
