import pandas as pd

FALLBACK_SPEED_KMH = 70

def _get_distancia(origem_cod, destino_cod, modal, distancias_df):
    if distancias_df.empty:
        return None
    filtro = distancias_df[
        (distancias_df["origem_codigo_ibge"] == str(origem_cod)) &
        (distancias_df["destino_codigo_ibge"] == str(destino_cod)) &
        (distancias_df["modal"] == modal)
    ]
    if filtro.empty:
        filtro = distancias_df[
            (distancias_df["origem_codigo_ibge"] == str(origem_cod)) &
            (distancias_df["destino_codigo_ibge"] == str(destino_cod))
        ]
    if not filtro.empty:
        return filtro.iloc[0]["distancia_km"]
    return None

def calcular_frete(
    origem_row, destino_row,
    modal, tipo_veiculo, tipo_carga,
    peso_kg, volume_m3, valor_carga,
    distancias_df, veiculos_df, cargas_df, modal_df, adicionais
):
    veiculo = veiculos_df[veiculos_df["tipo_veiculo"] == tipo_veiculo].iloc[0]
    carga = cargas_df[cargas_df["tipo_carga"] == tipo_carga].iloc[0]
    modal_row = modal_df[modal_df["modal"] == modal].iloc[0]

    distancia_km = _get_distancia(
        origem_row["codigo_municipio_ibge"],
        destino_row["codigo_municipio_ibge"],
        modal,
        distancias_df
    )
    fonte_distancia = "REGIC/IBGE"
    if distancia_km is None:
        distancia_km = 500.0
        fonte_distancia = "fallback estimado"

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

    if peso_kg <= capacidade_kg:
        adicional_peso = 0.0
    else:
        adicional_peso = (peso_kg - capacidade_kg) * taxa_excesso_kg

    seguro = max(valor_carga * fator_seguro, seguro_minimo)
    adicional_risco = custo_base * (fator_risco - 1.0)

    subtotal = custo_base + custo_fixo + carga_descarga + adicional_peso + seguro + adicional_risco
    taxa_administrativa = subtotal * taxa_adm_pct
    frete_estimado = max(subtotal + taxa_administrativa, frete_minimo)

    memoria = [
        {"item": "Distancia (km)", "valor": round(distancia_km, 2), "fonte": fonte_distancia},
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
        "distancia_km": distancia_km,
        "custo_base": round(custo_base, 2),
        "seguro": round(seguro, 2),
        "adicional_peso": round(adicional_peso, 2),
        "adicional_risco": round(adicional_risco, 2),
        "taxa_administrativa": round(taxa_administrativa, 2),
        "frete_estimado": round(frete_estimado, 2),
        "memoria_calculo": memoria,
    }
