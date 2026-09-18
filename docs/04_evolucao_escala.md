# Evolução para aplicação em escala

## Novos dados

- imagens recorrentes obtidas por veículos de inspeção;
- inspeções em campo associadas a quilômetro, sentido e data;
- histórico de poda, roçada, quedas e ordens de serviço;
- séries Sentinel-2 com várias observações por estação;
- chuva, vento, relevo e espécie vegetal quando disponíveis;
- largura oficial da faixa de domínio.

## Pipeline operacional

1. Agendar consultas de satélite após novas aquisições.
2. Manter banco geográfico com segmentos, imagens e histórico.
3. Calcular séries temporais e detectar mudanças persistentes.
4. Integrar fotografias rodoviárias para confirmar interferência visual.
5. Encaminhar os locais priorizados para revisão humana.
6. Registrar a inspeção e usar o retorno como novo rótulo.
7. Treinar modelo supervisionado somente com rótulos independentes.
8. Publicar prioridades em painel GIS com explicação e data.

## Atualização e monitoramento

- atualização mensal na estação de maior crescimento e trimestral nas demais;
- execução extraordinária após tempestades ou ventos severos;
- monitoramento de dados ausentes, nuvens e mudança de sensores;
- avaliação por rodovia, região, estação e classe;
- revisão periódica dos limiares com especialistas;
- auditoria de falsos negativos e decisões humanas.

## Condições para uso real

- validação de campo representativa;
- critérios definidos pela área de conservação e segurança;
- cobertura de diferentes tipos de vegetação e rodovia;
- desempenho medido em locais e datas independentes;
- rastreabilidade das versões de dados, regras e modelos;
- conformidade com licenças, contratos e políticas de privacidade.
