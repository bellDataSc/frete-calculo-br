import streamlit as st
import pandas as pd
from src.load_data import load_municipios, load_distancias, load_veiculos, load_cargas, load_modal, load_adicionais
from src.freight_calculator import calcular_frete
from src.validators import validar_entrada

st.set_page_config(page_title="frete-calculo-br", layout="wide")
st.title("Calculadora de Frete Intermunicipal")
st.caption("Estimativa baseada em dados publicos brasileiros — IBGE / REGIC / DNIT SICRO")

municipio_df = load_municipios()
distancias_df = load_distancias()
veiculos_df = load_veiculos()
cargas_df = load_cargas()
modal_df = load_modal()
adicionais = load_adicionais()

tab1, tab2, tab3 = st.tabs(["Simulador", "Distancias", "Parametros"])

with tab1:
    st.subheader("Simulador de Frete")
    col1, col2 = st.columns(2)

    with col1:
        municipios_lista = municipio_df["nome_municipio"].sort_values().tolist()
        origem_nome = st.selectbox("Municipio de Origem", municipios_lista, key="origem")
        destino_nome = st.selectbox("Municipio de Destino", municipios_lista, key="destino")
        modal_opcoes = modal_df["modal"].tolist()
        modal_selecionado = st.selectbox("Modal", modal_opcoes)

    with col2:
        veiculo_opcoes = veiculos_df["tipo_veiculo"].tolist()
        veiculo_selecionado = st.selectbox("Tipo de Veiculo", veiculo_opcoes)
        carga_opcoes = cargas_df["tipo_carga"].tolist()
        carga_selecionada = st.selectbox("Tipo de Carga", carga_opcoes)
        peso_kg = st.number_input("Peso (kg)", min_value=1.0, value=100.0)
        volume_m3 = st.number_input("Volume (m3)", min_value=0.01, value=1.0)
        valor_carga = st.number_input("Valor da Carga (R$)", min_value=0.0, value=1000.0)

    if st.button("Calcular Frete"):
        origem_row = municipio_df[municipio_df["nome_municipio"] == origem_nome].iloc[0]
        destino_row = municipio_df[municipio_df["nome_municipio"] == destino_nome].iloc[0]

        erros = validar_entrada(
            origem_row["codigo_municipio_ibge"],
            destino_row["codigo_municipio_ibge"],
            peso_kg,
            valor_carga,
            veiculos_df,
            veiculo_selecionado
        )

        if erros:
            for e in erros:
                st.error(e)
        else:
            resultado = calcular_frete(
                origem_row, destino_row,
                modal_selecionado, veiculo_selecionado, carga_selecionada,
                peso_kg, volume_m3, valor_carga,
                distancias_df, veiculos_df, cargas_df, modal_df, adicionais
            )

            st.subheader("Resultado")
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                st.metric("Distancia (km)", f"{resultado['distancia_km']:.1f}")
                st.metric("Custo Base (R$)", f"{resultado['custo_base']:.2f}")
                st.metric("Seguro (R$)", f"{resultado['seguro']:.2f}")
                st.metric("Adicional Peso (R$)", f"{resultado['adicional_peso']:.2f}")
            with col_r2:
                st.metric("Adicional Risco (R$)", f"{resultado['adicional_risco']:.2f}")
                st.metric("Taxa Administrativa (R$)", f"{resultado['taxa_administrativa']:.2f}")
                st.metric("Frete Estimado (R$)", f"{resultado['frete_estimado']:.2f}")

            st.subheader("Memoria de Calculo")
            st.dataframe(pd.DataFrame(resultado["memoria_calculo"]))

with tab2:
    st.subheader("Consulta de Distancias")
    if not distancias_df.empty:
        st.dataframe(distancias_df.head(100))
    else:
        st.info("Arquivo distancias_regic.csv nao encontrado em data/. Consulte instructions/data_sources.md.")

with tab3:
    st.subheader("Parametros do Calculo")
    st.markdown("**Veiculos**")
    st.dataframe(veiculos_df)
    st.markdown("**Tipos de Carga**")
    st.dataframe(cargas_df)
    st.markdown("**Modais**")
    st.dataframe(modal_df)
    st.markdown("**Adicionais**")
    st.dataframe(adicionais)
