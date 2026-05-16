import requests
import pandas as pd
import os
import time

IBGE_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "municipios_ibge.csv")
MAX_RETRIES = 3
RETRY_DELAY = 5

def extract_municipios():
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"Tentativa {attempt}/{MAX_RETRIES}...")
            response = requests.get(IBGE_URL, timeout=30, headers={"Accept": "application/json"})
            response.raise_for_status()

            if not response.text.strip():
                raise ValueError(f"Resposta vazia da API IBGE (status {response.status_code})")

            data = response.json()

            if not isinstance(data, list) or len(data) == 0:
                raise ValueError("Resposta da API nao contem uma lista de municipios valida")

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
            print(f"{len(df)} municipios salvos em {OUT_PATH}")
            return df

        except (requests.exceptions.RequestException, ValueError) as e:
            last_error = e
            print(f"Erro na tentativa {attempt}: {e}")
            if attempt < MAX_RETRIES:
                print(f"Aguardando {RETRY_DELAY}s antes de tentar novamente...")
                time.sleep(RETRY_DELAY)

    raise RuntimeError(
        f"Falha ao extrair municipios apos {MAX_RETRIES} tentativas. Ultimo erro: {last_error}\n"
        f"Verifique sua conexao e tente: curl '{IBGE_URL}' para confirmar se a API esta acessivel."
    )

if __name__ == "__main__":
    extract_municipios()
