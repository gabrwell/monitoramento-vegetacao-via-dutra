# Priorização de inspeções de vegetação na Via Dutra com dados Sentinel-2

**Turma:** 2CCPG

| Integrante | RM |
|---|---:|
| Pedro Henrique dos Santos Cardoso | 563268 |
| Gabriel Gibin Leoncio | 565462 |
| Rafael do Nascimento Silva | 566263 |
| Rai Augusto Ribeiro | 562870 |
| Guilherme Morais de Assis | 564198 |
| Lucas Werpp Franco | 556044 |

## Resumo

Este trabalho apresenta uma prova de conceito de Ciência de Dados para apoiar a
priorização de inspeções de vegetação na BR-116, entre Jacareí e São José dos
Campos. Foram combinados o traçado público da rodovia e cenas reais Sentinel-2
L2A de agosto de 2024 e agosto de 2025. O pipeline automatizado gerou 92 pontos
espacialmente distribuídos, calculou indicadores NDVI em um raio de 60 m e
construiu 184 observações tabulares. Uma regra explicável produziu rótulos proxy
de prioridade: 65 pontos baixos, 22 médios e 5 altos. A solução demonstra coleta,
preparação, análise, rotulagem e visualização reproduzíveis, mas não substitui
vistoria de campo, pois a resolução espacial e a falta de rótulos especializados
impedem afirmar risco rodoviário real.

## 1. Introdução

A gestão da vegetação ao longo de rodovias exige acompanhamento contínuo para
planejar inspeções e intervenções. Como não há recursos previstos para uma nova
campanha de coleta em campo, o desafio propõe o uso de dados reais provenientes
de fontes públicas e APIs. Além do resultado analítico, são centrais a automação
do pipeline, as decisões metodológicas e a discussão das limitações.

O projeto utiliza dados geográficos e uma pequena série temporal de satélite.
Essa alternativa é compatível com o caminho tabular sugerido no enunciado e
permite trabalhar com centenas de observações sem fabricar registros.

## 2. Pergunta e objetivos

Pergunta: **quais pontos da BR-116 apresentam maior presença ou aumento de
vegetação no entorno imediato e devem ser priorizados para inspeção?**

O objetivo foi construir um pipeline capaz de obter cenas reais, preparar dados,
calcular indicadores de vegetação, criar rótulos explicáveis e apresentar os
resultados em tabela, gráficos e mapa.

## 3. Dados

O eixo auxiliar da BR-116 foi obtido do OpenStreetMap por consulta automatizada
ao Overpass. A referência institucional da malha é o Sistema Nacional de Viação
do DNIT. O recorte pertence à Via Dutra, administrada pela CCR RioSP/Motiva.

As imagens são do Sentinel-2 L2A, consultadas na API STAC do Microsoft Planetary
Computer. O Sentinel-2 disponibiliza bandas visíveis e de infravermelho próximo
com resolução de 10 m. Foram utilizadas as bandas B04, B08 e a camada SCL de
classificação da cena.

Foram selecionadas quatro cenas:

- 23/08/2024: tiles 23KLQ e 23KMQ;
- 13/08/2025: tiles 23KLQ e 23KMQ.

As coberturas de nuvens declaradas variaram de aproximadamente 0,002% a 1,887%.
Os identificadores completos permanecem registrados para auditoria.

## 4. Método

Foram selecionados 92 pontos nas pistas classificadas como `motorway`, com
distância mínima aproximada de 150 m. Em cada data, as bandas foram lidas apenas
no recorte necessário. Pixels sem dados, saturados, com sombra, nuvem, cirrus ou
neve foram excluídos com a camada SCL.

O NDVI foi calculado por `(B08 − B04) / (B08 + B04)`. Para cada ponto foram
extraídos, em um raio de 60 m, média, mediana, percentil 90, fração de vegetação
densa e qualidade dos pixels. O percentil 90 representa a parte mais vegetada da
janela sem depender de um único valor extremo, reduzindo a diluição causada pelo
pavimento no centro.

O rótulo proxy foi definido antes da análise final:

- alta: NDVI p90 em 2025 ≥ 0,40 ou aumento do NDVI médio ≥ 0,05;
- média: NDVI p90 em 2025 ≥ 0,30 ou aumento ≥ 0,025;
- baixa: demais pontos.

Não foram usados quantis para balancear artificialmente as classes.

## 5. Dataset construído

O dataset longo possui 184 linhas, correspondentes a 92 pontos em duas datas.
Todos os pontos tiveram observações comparáveis e a fração média de pixels
válidos foi 100% nos recortes analisados. A base final possui uma linha por ponto,
com atributos dos dois anos, variação temporal, índice, classe e justificativa.

## 6. Resultados

O NDVI médio geral foi 0,1504 em 2024 e 0,1440 em 2025. A variação média foi
−0,0064 e a mediana −0,0046, não indicando crescimento generalizado no trecho.

A distribuição foi:

- baixa: 65 pontos (70,7%);
- média: 22 pontos (23,9%);
- alta: 5 pontos (5,4%).

Os pontos P070, P088, P087 e P035 foram classificados como altos principalmente
pelo NDVI p90 atual. O P057 foi classificado pelo aumento de 0,0508 no NDVI
médio. Esses cinco locais constituem candidatos para uma primeira inspeção, não
confirmações de perigo ou necessidade de manutenção.

## 7. Avaliação

Não foi treinado um modelo supervisionado, pois o projeto não possui rótulos
independentes de campo. Usar os próprios indicadores que criaram as classes para
treinar e avaliar um classificador produziria resultado circular.

A avaliação considerou completude espacial e temporal, validade de pixels,
distribuição das classes, rastreabilidade da fonte, reprodutibilidade da regra e
inspeção dos casos extremos. A classe alta permaneceu minoritária, refletindo o
resultado da regra nos dados reais.

## 8. Limitações

A resolução de 10 m não permite observar galhos, placas ocultas, árvores
inclinadas ou invasão do acostamento. O raio de 60 m combina rodovia, vegetação e
usos do solo vizinhos. Duas datas não estabelecem tendência de crescimento e,
mesmo em meses equivalentes, umidade, iluminação, atmosfera e fenologia variam.

A geometria pública pode conter pistas paralelas muito próximas. A cobertura de
nuvens é informada para o tile e não somente para a área de estudo. Finalmente,
o rótulo foi criado pelo grupo e não validado por especialista. Por isso, o
produto é adequado apenas como triagem acadêmica.

## 9. Evolução

Uma aplicação real deve integrar inspeções de campo, fotografias recorrentes,
histórico de manutenção, clima e uma série temporal maior. O retorno das equipes
de conservação deve gerar rótulos independentes. Somente então seria adequado
treinar e avaliar um modelo supervisionado.

O pipeline poderia ser executado mensalmente na estação de maior crescimento,
trimestralmente nos demais períodos e após eventos meteorológicos severos. Os
resultados deveriam alimentar um painel geográfico e permanecer sujeitos à
decisão humana.

## 10. Conclusão

A prova de conceito demonstrou que dados públicos reais podem ser coletados e
processados automaticamente para organizar uma fila de inspeção de vegetação.
Foram construídas 184 observações, 92 pontos comparáveis e cinco candidatos de
alta prioridade. O trabalho atende ao objetivo de demonstrar o pipeline e suas
decisões, mas também mostra que dados de satélite isolados não são suficientes
para diagnosticar risco. O próximo passo indispensável é validar os candidatos
em campo e usar essas inspeções para melhorar os critérios e medir desempenho.

## Referências

- EUROPEAN SPACE AGENCY. *Sentinel-2 Facts and Figures*.
- MICROSOFT. *Planetary Computer STAC API*.
- OPENSTREETMAP CONTRIBUTORS. *OpenStreetMap data and copyright*.
- DEPARTAMENTO NACIONAL DE INFRAESTRUTURA DE TRANSPORTES. *Sistema Nacional de Viação*.
- MOTIVA. *CCR RioSP — Via Dutra e Rio-Santos*.
