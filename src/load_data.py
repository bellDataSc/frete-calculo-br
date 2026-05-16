import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def _path(filename):
    return os.path.join(DATA_DIR, filename)

def load_municipios():
    path = _path("municipios_ibge.csv")
    if os.path.exists(path):
        return pd.read_csv(path, dtype={"codigo_municipio_ibge": str})
    return pd.DataFrame(columns=["codigo_municipio_ibge", "nome_municipio", "uf", "regiao"])

def load_distancias():
    path = _path("distancias_regic.csv")
    if os.path.exists(path):
        return pd.read_csv(path, dtype={"origem_codigo_ibge": str, "destino_codigo_ibge": str})
    return pd.DataFrame(columns=["origem_codigo_ibge", "destino_codigo_ibge", "distancia_km", "tempo_estimado", "modal"])

def load_veiculos():
    return pd.read_csv(_path("parametros_veiculos.csv"))

def load_cargas():
    return pd.read_csv(_path("parametros_cargas.csv"))

def load_modal():
    return pd.read_csv(_path("parametros_modal.csv"))

def load_adicionais():
    df = pd.read_csv(_path("adicionais.csv"))
    return dict(zip(df["parametro"], df["valor"]))
