import sys
import unittest
from pathlib import Path

import numpy as np
from affine import Affine
from rasterio.crs import CRS

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from verde_rodovias.geometria import (  # noqa: E402
    distancia_ponto_segmento_m,
    haversine_m,
    validar_bbox,
)
from verde_rodovias.satelite import gerar_pontos_rota, medir_ponto  # noqa: E402


class GeometriaTests(unittest.TestCase):
    def test_bbox_valida(self):
        self.assertEqual(
            validar_bbox([-46.2, -23.3, -45.7, -23.0]),
            (-46.2, -23.3, -45.7, -23.0),
        )

    def test_haversine_um_grau(self):
        distancia = haversine_m((0, 0), (0, 1))
        self.assertGreater(distancia, 111_000)
        self.assertLess(distancia, 112_000)

    def test_distancia_ponto_sobre_segmento(self):
        distancia = distancia_ponto_segmento_m(
            (-46.0, -23.2), (-46.1, -23.2), (-45.9, -23.2)
        )
        self.assertLess(distancia, 0.01)


class SateliteTests(unittest.TestCase):
    def test_gera_pontos_reais_sem_exceder_limite(self):
        pontos = gerar_pontos_rota(
            ROOT / "data/external/osm_br116_sjc.geojson",
            distancia_minima_m=150,
            max_pontos=100,
        )
        self.assertEqual(len(pontos), 92)
        self.assertEqual(pontos[0]["ponto_id"], "P001")

    def test_metricas_de_janela(self):
        # Matriz controlada apenas para teste unitário; não integra o dataset.
        ndvi = np.full((21, 21), 0.4, dtype="float32")
        ndvi[0, 0] = np.nan
        recorte = {
            "ndvi": ndvi,
            "transform": Affine(10, 0, 400000, 0, -10, 7500000),
            "crs": CRS.from_epsg(32723),
            "resolucao_m": 10,
        }
        from pyproj import Transformer

        transformer = Transformer.from_crs(32723, 4326, always_xy=True)
        longitude, latitude = transformer.transform(400105, 7499895)
        resultado = medir_ponto(
            recorte,
            longitude,
            latitude,
            raio_m=30,
            limite_vegetacao_densa=0.3,
        )
        self.assertIsNotNone(resultado)
        self.assertAlmostEqual(resultado["ndvi_media"], 0.4, places=5)
        self.assertAlmostEqual(resultado["fracao_vegetacao_densa"], 1.0, places=5)


if __name__ == "__main__":
    unittest.main()
