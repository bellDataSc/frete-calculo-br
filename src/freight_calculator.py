import math
import requests
import pandas as pd

OSRM_URL = "http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"
OSRM_TIMEOUT = 10


def _haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def _get_distancia_osrm(lat1, lon1, lat2, lon2):
    url = OSRM_URL.format(lat1=lat1, lon1=lon1, lat2=lat2, lon2=lon2)
    resp = requests.get(url, timeout=OSRM_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != "Ok":
        raise ValueError(f"OSRM retornou code={data.get('code')}")
    distancia_m = data["routes"][0]["distance"]
    duracao_s = data["routes"][0]["duration"]
    return distancia_m / 1000.0, duracao_s / 3600.0


def calcular_distancia(origem_row, destino_row):
    try:
        lat1 = float(origem_row["latitude"])
        lon1 = float(origem_row["longitude"])
        lat2 = float(destino_row["latitude"])
        lon2 = float(destino_row["longitude"])
    except (KeyError, TypeError, ValueError):
        return None, None, "coordenadas ausentes"

    try:
        distancia_km, duracao_h = _get_distancia_osrm(lat1, lon1, lat2, lon2)
        return distancia_km, duracao_h, "OSRM (rota rodoviaria real)"
    except Exception:
        pass

    distancia_km = _haversine(lat1, lon1, lat2, lon2)
    distancia_km = round(distancia_km * 1.25, 2)
    return distancia_km, None, "haversine +25% (estimativa, OSRM indisponivel)"


def calcular_frete(
    origem_row, destino_row,
    modal, tipo_veiculo, tipo_carga,
    peso_kg, volume_m3, valor_carga,
    distancias_df, veiculos_df, cargas_df, modal_df, adicionais
):
    veiculo = veiculos_df[veiculos_df["tipo_veiculo"] == tipo_veiculo].iloc[0]
    carga = cargas_df[cargas_df["tipo_carga"] == tipo_carga].iloc[0]
    modal_row = modal_df[modal_df["modal"] == modal].iloc[0]

    distancia_km, duracao_h, fonte_distancia = calcular_distancia(origem_row, destino_row)

    if distancia_km is None:
        distancia_km = 500.0
        fonte_distancia = "fallback fixo (coordenadas nao disponiveis)"

    custo_km_base = float(veiculo["custo_km_base"])
    fator_modal = float(modal_row["fator_modal"])
    fator_risco = float(carga["fator_risco"])
    fator_seguro = float(carga["fator_seguro"])
    capacidade_kg = float(veiculo["capacidade_kg"])
    frete_minimo = float(veiculo["frete_minimo"])

    custo_fixo = float(adicionais.get("custo_fixo_operacional", 120))
    carga_descarga = float(adicionais.get("carga_descarga_base", 80))
    taxa_adm_pct = float(adicionais.get("taxa_administrativa_percentual", 0.05))
    seguro_minimo = float(adicionais.get("seguro_minimo", 20))
    taxa_excesso_kg = float(adicionais.get("taxa_excesso_kg", 0.15))

    custo_base = distancia_km * custo_km_base * fator_modal

    adicional_peso = 0.0
    if peso_kg > capacidade_kg:
        adicional_peso = (peso_kg - capacidade_kg) * taxa_excesso_kg

    seguro = max(valor_carga * fator_seguro, seguro_minimo)
    adicional_risco = custo_base * (fator_risco - 1.0)

    subtotal = custo_base + custo_fixo + carga_descarga + adicional_peso + seguro + adicional_risco
    taxa_administrativa = subtotal * taxa_adm_pct
    frete_estimado = max(subtotal + taxa_administrativa, frete_minimo)

    tempo_str = f"{duracao_h:.1f}h" if duracao_h else "n/d"

    memoria = [
        {"item": "Municipio origem", "valor": origem_row["nome_municipio"], "fonte": "municipios_ibge.csv"},
        {"item": "Municipio destino", "valor": destino_row["nome_municipio"], "fonte": "municipios_ibge.csv"},
        {"item": "Distancia (km)", "valor": round(distancia_km, 2), "fonte": fonte_distancia},
        {"item": "Tempo estimado", "valor": tempo_str, "fonte": fonte_distancia},
        {"item": "Custo por km (R$)", "valor": custo_km_base, "fonte": "parametros_veiculos.csv"},
        {"item": "Fator modal", "valor": fator_modal, "fonte": "parametros_modal.csv"},
        {"item": "Custo base (R$)", "valor": round(custo_base, 2), "fonte": "calculo"},
        {"item": "Custo fixo operacional (R$)", "valor": custo_fixo, "fonte": "adicionais.csv"},
        {"item": "Carga e descarga (R$)", "valor": carga_descarga, "fonte": "adicionais.csv"},
        {"item": "Adicional peso (R$)", "valor": round(adicional_peso, 2), "fonte": "calculo"},
        {"item": "Seguro (R$)", "valor": round(seguro, 2), "fonte": "calculo"},
        {"item": "Adicional risco (R$)", "valor": round(adicional_risco, 2), "fonte": "calculo"},
        {"item": "Subtotal (R$)", "valor": round(subtotal, 2), "fonte": "calculo"},
        {"item": "Taxa administrativa (R$)", "valor": round(taxa_administrativa, 2), "fonte": "calculo"},
        {"item": "Frete minimo do veiculo (R$)", "valor": frete_minimo, "fonte": "parametros_veiculos.csv"},
        {"item": "Frete estimado final (R$)", "valor": round(frete_estimado, 2), "fonte": "max(subtotal+taxa, frete_minimo)"},
    ]

    return {
        "distancia_km": round(distancia_km, 2),
        "duracao_h": tempo_str,
        "fonte_distancia": fonte_distancia,
        "custo_base": round(custo_base, 2),
        "seguro": round(seguro, 2),
        "adicional_peso": round(adicional_peso, 2),
        "adicional_risco": round(adicional_risco, 2),
        "taxa_administrativa": round(taxa_administrativa, 2),
        "frete_estimado": round(frete_estimado, 2),
        "memoria_calculo": memoria,
    }
