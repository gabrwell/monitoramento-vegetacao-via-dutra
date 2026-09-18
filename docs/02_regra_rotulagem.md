# Regra de rotulagem

## Por que o rótulo é um proxy

As cenas de satélite informam a resposta espectral da superfície, mas não trazem
um rótulo de risco rodoviário. Sem inspeção de campo ou histórico de manutenção,
não existe classe verdadeira disponível. O grupo, portanto, construiu um rótulo
reproduzível de **prioridade para inspeção**.

## Indicadores usados

### NDVI

O índice é calculado por:

`NDVI = (B08 − B04) / (B08 + B04)`

Em que B08 é o infravermelho próximo e B04 é o vermelho do Sentinel-2. As duas
bandas possuem resolução de 10 m.

### Percentil 90

O centro da janela contém pavimento, que reduz a média de NDVI. O percentil 90
foi usado para representar a parte mais vegetada do entorno sem depender de um
único pixel extremo.

### Variação temporal

`delta_ndvi = NDVI médio de 2025 − NDVI médio de 2024`

As datas foram escolhidas no mesmo período do ano para reduzir, sem eliminar,
efeitos sazonais.

## Classes fixas

- **Alta:** NDVI p90 de 2025 ≥ 0,40 **ou** aumento do NDVI médio ≥ 0,05.
- **Média:** NDVI p90 de 2025 ≥ 0,30 **ou** aumento do NDVI médio ≥ 0,025.
- **Baixa:** demais pontos.

A regra foi aplicada igualmente a todos os registros. Não foram usados quantis
para forçar classes balanceadas.

## Índice para ordenação

Além da classe, um índice de 0 a 100 combina presença de vegetação no período
atual e variação temporal. Ele serve apenas para ordenar pontos dentro das
classes. A classe continua sendo determinada pelos limiares acima.

## Qualidade do rótulo

Vantagens:

- completamente reproduzível;
- justificativa armazenada em cada linha;
- não depende de avaliação visual inconsistente;
- pode ser recalculado quando os limiares forem revisados.

Limitações:

- não foi validado por engenheiro florestal ou equipe de conservação;
- mede sinal espectral, não interferência física na pista;
- os limiares são critérios de triagem, não normas operacionais;
- uma futura base de inspeções pode mudar as variáveis e as classes.
