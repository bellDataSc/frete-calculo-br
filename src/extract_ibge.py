import requests
import pandas as pd
import os
import time

IBGE_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
BRASIL_API_URL = "https://brasilapi.com.br/api/ibge/municipios/v1/{uf}?providers=ibge"
COORD_URL = "https://brasilapi.com.br/api/ibge/municipios/v1/{codigo}?providers=ibge"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search?q={municipio}+{uf}+Brasil&format=json&limit=1"
UFS = [
    "AC","AL","AM","AP","BA","CE","DF","ES","GO","MA",
    "MG","MS","MT","PA","PB","PE","PI","PR","RJ","RN",
    "RO","RR","RS","SC","SE","SP","TO"
]
REGIAO_MAP = {
    "AC":"Norte","AM":"Norte","AP":"Norte","PA":"Norte","RO":"Norte","RR":"Norte","TO":"Norte",
    "AL":"Nordeste","BA":"Nordeste","CE":"Nordeste","MA":"Nordeste","PB":"Nordeste",
    "PE":"Nordeste","PI":"Nordeste","RN":"Nordeste","SE":"Nordeste",
    "DF":"Centro-Oeste","GO":"Centro-Oeste","MS":"Centro-Oeste","MT":"Centro-Oeste",
    "ES":"Sudeste","MG":"Sudeste","RJ":"Sudeste","SP":"Sudeste",
    "PR":"Sul","RS":"Sul","SC":"Sul"
}
COORDS_CSV = "https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/municipios.csv"
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
                    "regiao": m["microrregiao"]["mesorregiao"]["UF"]["regiao"]["nome"],
                    "latitude": m.get("latitude", None),
                    "longitude": m.get("longitude", None)
                })
            return pd.DataFrame(rows)
        except Exception as e:
            last_error = e
            print(f"Erro: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
    raise RuntimeError(f"IBGE API falhou apos {MAX_RETRIES} tentativas: {last_error}")


def _extract_from_brasilapi():
    print("Usando BrasilAPI por UF...")
    rows = []
    for uf in UFS:
        url = BRASIL_API_URL.format(uf=uf)
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            municipios = resp.json()
            for m in municipios:
                rows.append({
                    "codigo_municipio_ibge": str(m["codigo_ibge"]),
                    "nome_municipio": m["nome"],
                    "uf": uf,
                    "regiao": REGIAO_MAP.get(uf, ""),
                    "latitude": None,
                    "longitude": None
                })
            print(f"  {uf}: {len(municipios)} municipios")
        except Exception as e:
            print(f"  {uf}: erro - {e}")
        time.sleep(0.2)
    if len(rows) == 0:
        raise RuntimeError("BrasilAPI nao retornou nenhum municipio")
    return pd.DataFrame(rows)


def _enrich_coords_from_kelvins(df):
    print("\nEnriquecendo coordenadas via mirror kelvins/municipios-brasileiros...")
    try:
        raw = pd.read_csv(COORDS_CSV, dtype={"codigo_ibge": str})
        raw = raw.rename(columns={"codigo_ibge": "codigo_municipio_ibge"})
        merge = df.merge(
            raw[["codigo_municipio_ibge", "latitude", "longitude"]],
            on="codigo_municipio_ibge",
            how="left",
            suffixes=("", "_kelvins")
        )
        mask = df["latitude"].isna()
        df.loc[mask, "latitude"] = merge.loc[mask, "latitude_kelvins"]
        df.loc[mask, "longitude"] = merge.loc[mask, "longitude_kelvins"]
        filled = df["latitude"].notna().sum()
        print(f"  Coordenadas preenchidas: {filled}/{len(df)}")
    except Exception as e:
        print(f"  Aviso: nao foi possivel enriquecer coordenadas - {e}")
    return df


def extract_municipios():
    df = None
    source = None

    try:
        df = _extract_from_ibge()
        source = "IBGE Localidades API"
    except RuntimeError as e:
        print(f"\nIBGE API indisponivel: {e}")
        print("Tentando BrasilAPI...\n")
        try:
            df = _extract_from_brasilapi()
            source = "BrasilAPI por UF"
        except Exception as e2:
            raise RuntimeError(
                f"Todas as fontes falharam.\nIBGE: {e}\nBrasilAPI: {e2}"
            )

    if df["latitude"].isna().any():
        df = _enrich_coords_from_kelvins(df)

    df.to_csv(OUT_PATH, index=False)
    print(f"\n{len(df)} municipios salvos em {OUT_PATH}")
    print(f"Fonte: {source}")
    return df


if __name__ == "__main__":
    extract_municipios()
