# Data Sources

## IBGE Localidades

Provides the official list of Brazilian municipalities with IBGE codes, state (UF), and geographic region.

Endpoint: `https://servicodados.ibge.gov.br/api/v1/localidades/municipios`

Key fields used:
- `id` mapped to `codigo_municipio_ibge`
- `nome` mapped to `nome_municipio`
- `microrregiao.mesorregiao.UF.sigla` mapped to `uf`
- `microrregiao.mesorregiao.UF.regiao.nome` mapped to `regiao`

## IBGE/REGIC Distances

The REGIC (Regions of Influence of Cities) study from IBGE provides intermunicipal connections including road, waterway, and air distances between municipal seats.

The base covers approximately 71,000 intermunicipal connections.

Source: https://www.ibge.gov.br/geociencias/organizacao-do-territorio/redes-e-fluxos-geograficos/15798-regioes-de-influencia-das-cidades.html

This project uses the REGIC base for `data/distancias_regic.csv`. When no route is found, a fallback value is used and documented in the calculation memory.

## DNIT/SICRO

The SICRO (Sistema de Custos Referenciais de Obras) from DNIT is used as methodological reference for cost parameters per km, operational fixed costs, and handling fees.

This project does not replicate SICRO directly. The CSV files in `data/` contain simplified referential parameters inspired by the SICRO methodology.

Portal: https://www.gov.br/dnit/pt-br/assuntos/planejamento-e-pesquisa/custos-e-pagamentos/custos-e-pagamentos/sicro

## DNIT Open Data

Optional enrichment source. Contains datasets on pavement conditions, traffic counts, road jurisdiction, and weighing stations.

Access: https://dados.dnit.gov.br
