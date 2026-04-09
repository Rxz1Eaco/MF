import pandas as pd 
import streamlit as st 



st.title("Controles Serviços MA")



@st.cache_data
def carregar_dados():
    sheet_id = "1nT6I4SC7eMo8Oowk4g4ypLfHRQhSJeIIcbHXttZ1UW0"
    gid = "409250655"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

    df = pd.read_csv(
        url,
        sep=",",
        engine="python",
        encoding="utf-8",
        on_bad_lines="skip"
    )

    return df


df = carregar_dados()


df = df.drop(columns=['Carimbo de data/hora'])
# st.dataframe(df)


# Converter coluna para data
df["Dia"] = pd.to_datetime(df["Dia"])

# =========================
# FILTRO SIDEBAR
# =========================
st.sidebar.header("Filtros")

data_inicio = st.sidebar.date_input(
    "Data inicial",
    value=df["Dia"].min()
)

data_fim = st.sidebar.date_input(
    "Data final",
    value=df["Dia"].max()
)

tipos = df["Tipo"].dropna().unique()

filtro_tipo = st.sidebar.multiselect(
    "Tipo de Serviço:",
    options=tipos,
    default=tipos
)


# Aplicar filtro
df_filtrado = df[
    (df["Dia"] >= pd.to_datetime(data_inicio)) &
    (df["Dia"] <= pd.to_datetime(data_fim)) &
    (df["Tipo"].isin(filtro_tipo))
]




st.dataframe(df_filtrado)

if st.button("🔄 Atualizar Dados"):
    carregar_dados.clear()
    st.rerun()


st.markdown("### KPIs")
col1 , col2 = st.columns(2)
quantidade_inova = (df_filtrado["Tipo"] == "Inova").sum()
col1.metric("Serviços: Inova", quantidade_inova) 

quantidade_reboque = (df_filtrado["Tipo"] == "MF Reboque").sum()
col2.metric("Serviços: MF Reboque", quantidade_reboque) 

col1.metric(
    "Receita Total",
    f"R$ {df_filtrado['Valor Serviço'].sum():,.2f}"
)

st.markdown("### 📈 Serviços por Dia")

servicos_por_dia = df_filtrado.groupby("Dia").size()

st.line_chart(servicos_por_dia)

st.markdown("### 🏆 Ranking de Motoristas")

ranking_motoristas = (
    df_filtrado.groupby("Motorista")
    .size()
    .reset_index(name="Quantidade")
    .sort_values(by="Quantidade", ascending=False)
)

st.dataframe(ranking_motoristas)

st.bar_chart(ranking_motoristas.set_index("Motorista"))