# Dados

- `external/osm_br116_sjc.geojson`: traçado auxiliar real do OpenStreetMap.
- `raw/pontos_amostragem.csv`: 92 pontos gerados ao longo da rodovia.
- `raw/itens_sentinel.json`: identificadores e metadados das quatro cenas.
- `processed/observacoes_sentinel.csv`: 184 observações reais, antes da comparação.
- `processed/segmentos_priorizados.csv`: 92 pontos comparáveis e rotulados.

Os CSVs podem ser reproduzidos por `scripts/coletar_sentinel.py` e
`scripts/analisar_sentinel.py`. Nenhuma linha sintética é utilizada nos
resultados. Matrizes pequenas criadas nos testes servem apenas para validar o
código e não entram no dataset ou no relatório.
