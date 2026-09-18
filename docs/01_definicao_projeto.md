# Definição do projeto

## Contexto

Inspecionar continuamente toda a extensão de uma rodovia exige tempo e recursos.
Dados de sensoriamento remoto podem apoiar uma triagem inicial, destacando locais
com maior sinal de vegetação no entorno ou aumento do índice de vegetação entre
períodos comparáveis.

## Pergunta

Quais pontos da BR-116 apresentam maior presença ou aumento de vegetação no
entorno imediato e devem ser priorizados para inspeção?

## Objetivo geral

Construir uma prova de conceito automatizada que combine a geometria da rodovia
com imagens Sentinel-2, calcule indicadores de vegetação e produza uma lista
georreferenciada de prioridades para inspeção.

## Objetivos específicos

1. Obter um traçado público e real da BR-116.
2. Gerar pontos de amostragem espacialmente distribuídos.
3. Consultar cenas Sentinel-2 por API, data, área e cobertura de nuvens.
4. Calcular NDVI em uma vizinhança de 60 m ao redor de cada ponto.
5. Comparar agosto de 2024 com agosto de 2025 para reduzir diferenças sazonais.
6. Criar um rótulo proxy de prioridade por critérios fixos e explicáveis.
7. Gerar dataset, gráficos, tabela de prioridades e discussão das limitações.

## Recorte

- Rodovia: BR-116, Via Dutra.
- Região: Jacareí e São José dos Campos, SP.
- Concessionária: CCR RioSP, empresa Motiva.
- Coordenadas: bbox `[-46.15, -23.26, -45.75, -23.10]`.
- Unidade espacial: ponto no eixo das pistas principais.
- Espaçamento mínimo aproximado: 150 m.
- Raio de análise: 60 m.
- Datas: 23/08/2024 e 13/08/2025.

## Variáveis

- latitude e longitude;
- data, tile e identificador da cena;
- cobertura de nuvens declarada para a cena;
- quantidade e proporção de pixels válidos;
- NDVI médio, mediano e percentil 90;
- fração de pixels com NDVI igual ou superior a 0,5;
- variação do NDVI entre 2024 e 2025;
- índice e classe de prioridade.

## O que a solução afirma

A solução classifica a **prioridade de verificação** de um ponto em relação aos
demais critérios definidos. Ela não identifica espécie, altura, inclinação de
árvore, invasão do acostamento nem risco real de queda.
