# Setup

## Requirements

Python 3.10 or higher.

## Installation

```bash
pip install -r requirements.txt
```

## Running the app

```bash
streamlit run app.py
```

## Populating municipality data

The file `data/municipios_ibge.csv` is not committed to the repository because it is extracted from the IBGE Localidades API.

To generate it, run:

```bash
python src/extract_ibge.py
```

This will call `https://servicodados.ibge.gov.br/api/v1/localidades/municipios` and save the result to `data/municipios_ibge.csv`.

## Distance data

The file `data/distancias_regic.csv` must be populated manually from the IBGE/REGIC base.

Expected columns:

```
origem_codigo_ibge, destino_codigo_ibge, distancia_km, tempo_estimado, modal
```

When no distance record is found for an origin-destination pair, the calculator uses a fallback of 500 km and flags the source as "fallback estimado" in the calculation memory.
