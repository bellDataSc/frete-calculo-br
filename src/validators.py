def validar_entrada(origem_cod, destino_cod, peso_kg, valor_carga, veiculos_df, tipo_veiculo):
    erros = []

    if str(origem_cod) == str(destino_cod):
        erros.append("Municipio de origem e destino nao podem ser iguais.")

    if peso_kg <= 0:
        erros.append("Peso deve ser maior que zero.")

    if valor_carga < 0:
        erros.append("Valor da carga nao pode ser negativo.")

    veiculo_row = veiculos_df[veiculos_df["tipo_veiculo"] == tipo_veiculo]
    if veiculo_row.empty:
        erros.append(f"Tipo de veiculo '{tipo_veiculo}' nao encontrado nos parametros.")
    else:
        capacidade = float(veiculo_row.iloc[0]["capacidade_kg"])
        if peso_kg > capacidade * 3:
            erros.append(f"Peso informado ({peso_kg} kg) excede 3x a capacidade do veiculo ({capacidade} kg). Revise o tipo de veiculo.")

    return erros
