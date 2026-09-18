"""Operações geográficas leves, sem dependências externas."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Iterable, Sequence

EARTH_RADIUS_M = 6_371_008.8


def validar_bbox(valores: Sequence[float]) -> tuple[float, float, float, float]:
    """Valida bbox no formato min_lon, min_lat, max_lon, max_lat."""
    if len(valores) != 4:
        raise ValueError("A bbox deve conter quatro valores.")
    min_lon, min_lat, max_lon, max_lat = map(float, valores)
    if not (-180 <= min_lon < max_lon <= 180):
        raise ValueError("Longitudes inválidas na bbox.")
    if not (-90 <= min_lat < max_lat <= 90):
        raise ValueError("Latitudes inválidas na bbox.")
    return min_lon, min_lat, max_lon, max_lat


def haversine_m(a: Sequence[float], b: Sequence[float]) -> float:
    """Distância aproximada em metros entre dois pontos (lon, lat)."""
    lon1, lat1 = map(math.radians, a)
    lon2, lat2 = map(math.radians, b)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(h))


def _xy_local(ponto: Sequence[float], lat_ref: float) -> tuple[float, float]:
    lon, lat = ponto
    x = math.radians(lon) * EARTH_RADIUS_M * math.cos(math.radians(lat_ref))
    y = math.radians(lat) * EARTH_RADIUS_M
    return x, y


def distancia_ponto_segmento_m(
    ponto: Sequence[float], inicio: Sequence[float], fim: Sequence[float]
) -> float:
    """Distância plana local entre um ponto e um segmento geográfico."""
    lat_ref = (float(ponto[1]) + float(inicio[1]) + float(fim[1])) / 3
    px, py = _xy_local(ponto, lat_ref)
    ax, ay = _xy_local(inicio, lat_ref)
    bx, by = _xy_local(fim, lat_ref)
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def distancia_rotas_m(ponto: Sequence[float], rotas: Iterable[Sequence[Sequence[float]]]) -> float:
    """Menor distância do ponto a qualquer segmento das rotas."""
    menor = math.inf
    for rota in rotas:
        for inicio, fim in zip(rota, rota[1:]):
            menor = min(menor, distancia_ponto_segmento_m(ponto, inicio, fim))
    return menor


def carregar_rotas_geojson(caminho: str | Path) -> list[list[list[float]]]:
    """Carrega LineString e MultiLineString de um GeoJSON."""
    with Path(caminho).open("r", encoding="utf-8") as arquivo:
        objeto = json.load(arquivo)

    geometrias: list[dict] = []
    if objeto.get("type") == "FeatureCollection":
        geometrias = [f.get("geometry") or {} for f in objeto.get("features", [])]
    elif objeto.get("type") == "Feature":
        geometrias = [objeto.get("geometry") or {}]
    else:
        geometrias = [objeto]

    rotas: list[list[list[float]]] = []
    for geometria in geometrias:
        tipo = geometria.get("type")
        coordenadas = geometria.get("coordinates") or []
        if tipo == "LineString" and len(coordenadas) >= 2:
            rotas.append(coordenadas)
        elif tipo == "MultiLineString":
            rotas.extend(linha for linha in coordenadas if len(linha) >= 2)
    if not rotas:
        raise ValueError(f"Nenhuma linha válida encontrada em {caminho}.")
    return rotas
