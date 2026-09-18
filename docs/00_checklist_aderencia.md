# Checklist de aderência ao enunciado

| Requisito | Evidência no projeto | Situação |
|---|---|---|
| Pergunta de Ciência de Dados | Definida em `01_definicao_projeto.md` | Concluído |
| Fonte real de dados | Sentinel-2 L2A, Planetary Computer e OpenStreetMap | Concluído |
| Processo de coleta documentado | `scripts/coletar_sentinel.py` e documentação | Concluído |
| Dataset construído pelo grupo | 184 observações em `observacoes_sentinel.csv` | Concluído |
| Dataset rotulado | 92 pontos com prioridade e justificativa | Concluído |
| Dados não artificiais | Métricas calculadas diretamente das cenas públicas | Concluído |
| Automação | Da consulta STAC aos CSVs, gráficos e mapa | Concluído |
| Preparação e engenharia de atributos | Máscara de qualidade, NDVI, p90 e variação temporal | Concluído |
| Avaliação dos resultados | Cobertura, validade, distribuição e comparação temporal | Concluído |
| Discussão das limitações | Relatório e `03_analise_resultados.md` | Concluído |
| Proposta de maior escala | `04_evolucao_escala.md` | Concluído |
| Qualidade e representatividade | Discutidas com base nos resultados observados | Concluído |
| Atualização periódica | Proposta operacional documentada | Concluído |

## Caminho escolhido

O enunciado permite imagens, dados tabulares, dados geográficos, séries temporais
e combinações dessas fontes. Foi escolhido o caminho:

`API/base pública → coleta → tratamento → análise exploratória → engenharia de atributos`

A base final possui 184 linhas, atendendo à orientação de trabalhar com centenas
de registros em um projeto tabular. As quatro cenas Sentinel-2 usadas são reais e
estão identificadas em `data/raw/itens_sentinel.json`.

## Observação sobre os rótulos

Como não há inspeções de campo que forneçam uma classe verdadeira de risco, o
projeto cria um **rótulo proxy de prioridade** por uma regra transparente. Isso é
documentado como limitação; o rótulo não deve ser interpretado como diagnóstico
de segurança.
