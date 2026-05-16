# frete-calculo-br

I built this project to estimate intermunicipal freight costs in Brazil using public data sources. The calculation is based on official IBGE municipality codes, REGIC/IBGE intermunicipal distances, and referential cost parameters inspired by the DNIT/SICRO methodology.

I developed this automation to support internal logistics planning processes at my company. The goal is not to replace a commercial carrier quote, but to provide a transparent, auditable, and reproducible methodology for freight simulations in public studies, logistics planning, and budget analysis.

I attended a GitHub Copilot training at Microsoft Brazil and found it genuinely useful. I applied what I learned directly in this project, using Copilot to accelerate the development of the calculation engine, data loading modules, and Streamlit interface.

## Stack

- Python
- Streamlit
- Pandas
- Plotly
- SQLite
- Requests

## Data Sources

- IBGE Localidades API — official municipality list with IBGE codes
- IBGE/REGIC — intermunicipal distances (~71k connections)
- DNIT/SICRO — referential cost methodology
- DNIT Open Data — optional road context enrichment

## Project Structure

```
frete-calculo-br/
├── app.py
├── requirements.txt
├── data/
│   ├── parametros_veiculos.csv
│   ├── parametros_cargas.csv
│   ├── parametros_modal.csv
│   ├── adicionais.csv
│   ├── municipios_ibge.csv        # populated by extract_ibge.py
│   └── distancias_regic.csv       # populated manually or via REGIC base
├── src/
│   ├── freight_calculator.py
│   ├── load_data.py
│   ├── extract_ibge.py
│   └── validators.py
├── instructions/
│   ├── setup.md
│   ├── data_sources.md
│   ├── calculation_methodology.md
│   └── roadmap.md
├── notebooks/
│   └── 01_analise_distancias.ipynb
└── docs/
    └── memoria_calculo.md
```

## Versions

| Version | Scope |
|---|---|
| 0.1 | Streamlit app, CSV parameters, freight calculator with calculation memory |
| 0.2 | IBGE API extraction, SQLite storage, CSV export |
| 0.3 | UF dashboard, modal comparison, FastAPI, Streamlit Cloud deploy |

## Running Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```
