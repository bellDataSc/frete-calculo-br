import requests
import pandas as pd
import os

IBGE_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "municipios_ibge.csv")

def extract_municipios():
    response = requests.get(IBGE_URL, timeout=30)
    response.raise_for_status()
    data = response.json()

    rows = []
    for m in data:
        rows.append({
            "codigo_municipio_ibge": str(m["id"]),
            "nome_municipio": m["nome"],
            "uf": m["microrregiao"]["mesorregiao"]["UF"]["sigla"],
            "regiao": m["microrregiao"]["mesorregiao"]["UF"]["regiao"]["nome"]
        })

    df = pd.DataFrame(rows)
    df.to_csv(OUT_PATH, index=False)
    return df

if __name__ == "__main__":
    df = extract_municipios()
    print(f"{len(df)} municipios salvos em {OUT_PATH}")
