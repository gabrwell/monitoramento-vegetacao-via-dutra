# Análise e resultados

## Dataset

- 92 pontos planejados e medidos nos dois períodos;
- 184 observações reais antes da comparação;
- 92 linhas no dataset final, uma por ponto;
- validade média dos pixels: 100% nas duas datas;
- duas cenas por data, correspondentes aos tiles 23KLQ e 23KMQ.

As cenas de 2024 apresentaram aproximadamente 0,002% e 0,003% de nuvens. Em
2025, os valores foram aproximadamente 0,015% e 1,887%.

## Variação temporal

- NDVI médio geral em 2024: 0,1504;
- NDVI médio geral em 2025: 0,1440;
- variação média: −0,0064;
- variação mediana: −0,0046.

Não foi observado aumento generalizado do NDVI. A pequena redução média não deve
ser interpretada automaticamente como remoção de vegetação, pois diferenças de
umidade, iluminação, atmosfera e fenologia permanecem possíveis.

## Prioridades

| Classe | Pontos | Percentual |
|---|---:|---:|
| Baixa | 65 | 70,7% |
| Média | 22 | 23,9% |
| Alta | 5 | 5,4% |

Pontos de prioridade alta:

| Ponto | Longitude | Latitude | NDVI p90 2025 | Δ NDVI médio | Motivo principal |
|---|---:|---:|---:|---:|---|
| P070 | -45,792953 | -23,155950 | 0,456 | 0,010 | Presença |
| P088 | -45,757602 | -23,138151 | 0,445 | 0,009 | Presença |
| P057 | -45,829930 | -23,174504 | 0,384 | 0,051 | Aumento |
| P087 | -45,759290 | -23,138829 | 0,404 | 0,004 | Presença |
| P035 | -45,878462 | -23,199611 | 0,407 | -0,001 | Presença |

Esses locais são candidatos a verificação, não ocorrências confirmadas.

## Avaliação

Não foi treinado um classificador supervisionado, porque os rótulos foram
derivados dos próprios atributos. Treinar e medir um modelo contra esses rótulos
produziria uma avaliação circular. A prova de conceito foi avaliada por:

- completude espacial e temporal;
- proporção de pixels válidos;
- distribuição das classes;
- reprodutibilidade dos rótulos;
- coerência entre presença atual e variação temporal;
- inspeção dos pontos extremos e da tabela de prioridades.

## Limitações encontradas

- resolução de 10 m não mostra galhos, placas ou acostamento com precisão;
- a janela de 60 m mistura pista, vegetação, edificações e terrenos vizinhos;
- somente duas datas não caracterizam uma tendência de crescimento;
- as datas diferem em dez dias do calendário e podem refletir fenologia;
- cobertura de nuvens do item é uma estatística do tile inteiro;
- pontos em pistas paralelas podem representar áreas semelhantes;
- não há validação de campo nem rótulo fornecido por especialista;
- a classe alta é pequena, um desbalanceamento real que não foi corrigido.
