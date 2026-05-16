import requests
import pandas as pd
import os
import time

IBGE_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
BRASILIO_URL = "https://brasil.io/api/dataset/divida-ativa/municipios/data/?format=json&page_size=10000"
BRASILIO_CSV = "https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/municipios.csv"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "municipios_ibge.csv")
MAX_RETRIES = 3
RETRY_DELAY = 5


def _extract_from_ibge():
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"IBGE API - tentativa {attempt}/{MAX_RETRIES}...")
            response = requests.get(IBGE_URL, timeout=30, headers={"Accept": "application/json"})
            response.raise_for_status()
            if not response.text.strip():
                raise ValueError(f"Resposta vazia (status {response.status_code})")
            data = response.json()
            if not isinstance(data, list) or len(data) == 0:
                raise ValueError("Resposta nao contem lista valida")
            rows = []
            for m in data:
                rows.append({
                    "codigo_municipio_ibge": str(m["id"]),
                    "nome_municipio": m["nome"],
                    "uf": m["microrregiao"]["mesorregiao"]["UF"]["sigla"],
                    "regiao": m["microrregiao"]["mesorregiao"]["UF"]["regiao"]["nome"]
                })
            return pd.DataFrame(rows)
        except Exception as e:
            last_error = e
            print(f"Erro: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
    raise RuntimeError(f"IBGE API falhou apos {MAX_RETRIES} tentativas: {last_error}")


def _extract_from_github_mirror():
    print("Usando mirror GitHub (kelvins/municipios-brasileiros)...")
    response = requests.get(BRASILIO_CSV, timeout=30)
    response.raise_for_status()
    from io import StringIO
    df_raw = pd.read_csv(StringIO(response.text))
    df = pd.DataFrame({
        "codigo_municipio_ibge": df_raw["codigo_ibge"].astype(str),
        "nome_municipio": df_raw["nome"],
        "uf": df_raw["uf"],
        "regiao": df_raw["uf"]
    })
    return df


def extract_municipios():
    df = None
    source = None

    try:
        df = _extract_from_ibge()
        source = "IBGE Localidades API"
    except RuntimeError as e:
        print(f"\nIBGE API indisponivel. Motivo: {e}")
        print("Tentando mirror publico (GitHub/kelvins)...\n")
        try:
            df = _extract_from_github_mirror()
            source = "mirror GitHub kelvins/municipios-brasileiros"
        except Exception as e2:
            raise RuntimeError(
                f"Todas as fontes falharam.\n"
                f"IBGE: {e}\n"
                f"Mirror: {e2}\n\n"
                f"Tente manualmente:\n"
                f"  curl '{IBGE_URL}' | head -c 200"
            )

    df.to_csv(OUT_PATH, index=False)
    print(f"{len(df)} municipios salvos em {OUT_PATH}")
    print(f"Fonte: {source}")
    return df


if __name__ == "__main__":
    extract_municipios()
