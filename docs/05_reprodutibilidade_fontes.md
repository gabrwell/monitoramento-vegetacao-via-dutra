# Reprodutibilidade e fontes

## Ambiente

- Python 3.12 recomendado;
- dependências fixadas em `requirements.txt`;
- código compatível com VS Code, Jupyter e Google Colab;
- parâmetros centralizados em `config/projeto_satelite.json`.

## Sequência de reprodução

1. Instalar as dependências.
2. Executar `scripts/coletar_rota_osm.py` se o GeoJSON estiver ausente.
3. Executar `scripts/coletar_sentinel.py` com internet.
4. Executar `scripts/analisar_sentinel.py`.
5. Conferir `outputs/resumo_resultados.json` e os produtos gerados.

## Cenas utilizadas

Os identificadores completos, datas, tiles e cobertura de nuvens estão em
`data/raw/itens_sentinel.json`. Foram usadas duas cenas por data para cobrir os
tiles 23KLQ e 23KMQ.

## Acesso e autenticação

- Planetary Computer: consulta pública por API STAC e URLs de ativos assinadas
  automaticamente pelo pacote `planetary-computer`; sem serviço pago no projeto.
- OpenStreetMap/Overpass: consulta pública sem chave, com atribuição ODbL.
- DNIT: usado como referência institucional da malha rodoviária.
- Motiva/CCR RioSP: usada para contextualizar a concessão.

## Referências eletrônicas

- Microsoft. *Planetary Computer STAC API*. Disponível em:
  https://planetarycomputer.microsoft.com/docs/reference/stac/
- ESA. *Sentinel-2 Facts and Figures*. Disponível em:
  https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-2/Facts_and_figures
- OpenStreetMap. *Copyright and License*. Disponível em:
  https://www.openstreetmap.org/copyright
- DNIT. *Plano Nacional de Viação e Sistema Nacional de Viação*. Disponível em:
  https://www.gov.br/dnit/pt-br/assuntos/atlas-e-mapas/pnv-e-snv
- Motiva. *Sobre a CCR RioSP*. Disponível em:
  https://rodovias.motiva.com.br/riosp/sobre/sobre-riosp/
