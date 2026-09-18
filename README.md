# Monitoramento de vegetação na Via Dutra

[![Abrir no Google Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/gabrwell/monitoramento-vegetacao-via-dutra/blob/main/notebooks/01_projeto_final_colab.ipynb)

Prova de conceito de Ciência de Dados para priorizar inspeções de vegetação no
entorno da BR-116, entre Jacareí e São José dos Campos (SP), trecho administrado
pela CCR RioSP/Motiva.

## Pergunta de Ciência de Dados

> Quais pontos da BR-116 apresentam maior presença ou aumento de vegetação no
> entorno imediato e devem ser priorizados para inspeção?

A solução usa dados reais do Sentinel-2 L2A acessados pela API STAC do Microsoft
Planetary Computer. O traçado auxiliar da rodovia vem do OpenStreetMap. Nenhuma
observação de pesquisa foi criada artificialmente.

## Resultado da prova de conceito

- 92 pontos distribuídos pelas pistas principais da rodovia;
- duas medições comparáveis por ponto, em agosto de 2024 e agosto de 2025;
- 184 observações tabulares reais;
- 92 pontos com dados válidos nos dois períodos;
- 65 pontos de prioridade baixa, 22 média e 5 alta;
- três gráficos, tabela de pontos prioritários e dataset final rotulado.

As prioridades são indicadores para triagem. Não são laudos de risco e precisam
de validação em campo antes de qualquer decisão de manutenção.

## Arquivos principais

```text
notebooks/01_projeto_final_colab.ipynb       notebook para apresentação
relatorio/relatorio_final.docx               relatório final formatado
relatorio/relatorio_final.md                 texto completo do trabalho
data/processed/observacoes_sentinel.csv      184 observações reais
data/processed/segmentos_priorizados.csv     92 pontos rotulados
outputs/figures/                             gráficos da análise
scripts/coletar_sentinel.py                  aquisição e preparação
scripts/analisar_sentinel.py                 análise, rótulos e produtos
config/projeto_satelite.json                 decisões metodológicas
```

## Execução no VS Code

Requisito: Python 3.12. No PowerShell, dentro da pasta do projeto:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\coletar_sentinel.py
.\.venv\Scripts\python.exe scripts\analisar_sentinel.py
```

A coleta exige internet. A análise pode ser refeita usando os CSVs já incluídos.

## Execução no Google Colab

1. Clique no botão **Abrir no Google Colab** no início deste README.
2. No Colab, escolha **Ambiente de execução > Executar tudo**.
3. Aguarde a conclusão das células e confira as tabelas e os gráficos.

O notebook usa os dados reais incluídos. Há uma opção explícita para refazer a
coleta pela API. O próprio notebook baixa este repositório automaticamente; não
é necessário enviar ZIP, montar o Google Drive ou autorizar acesso a arquivos.
Na execução padrão, o Colab instala apenas as dependências leves de análise de
`requirements_colab.txt`. As bibliotecas geoespaciais completas são instaladas
somente se `REFAZER_COLETA` for alterado para `True`.

O mesmo arquivo `.ipynb` também pode ser aberto no Jupyter Notebook ou no VS Code
com a extensão Jupyter. O Colab é uma opção de execução, não uma exigência do
projeto.

## Documentação

- [Aderência ao enunciado](docs/00_checklist_aderencia.md)
- [Definição do projeto](docs/01_definicao_projeto.md)
- [Regra de rotulagem](docs/02_regra_rotulagem.md)
- [Plano e resultados da análise](docs/03_analise_resultados.md)
- [Evolução em escala](docs/04_evolucao_escala.md)
- [Reprodutibilidade e fontes](docs/05_reprodutibilidade_fontes.md)

## Fontes

- [Microsoft Planetary Computer — STAC API](https://planetarycomputer.microsoft.com/docs/reference/stac/)
- [ESA — Sentinel-2](https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-2/Facts_and_figures)
- [OpenStreetMap](https://www.openstreetmap.org/copyright)
- [DNIT — Sistema Nacional de Viação](https://www.gov.br/dnit/pt-br/assuntos/atlas-e-mapas/pnv-e-snv)
- [CCR RioSP/Motiva](https://rodovias.motiva.com.br/riosp/sobre/sobre-riosp/)
