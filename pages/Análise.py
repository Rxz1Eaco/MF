import pandas as pd
import streamlit as st

st.title("MF - AUTO SOCORRO")

# =========================
# CARREGAMENTO DOS DADOS
# =========================

# https://docs.google.com/spreadsheets/d/1Ez2ADJrTNzE2tCmlNpoGUsG29PtMVPDP1ZsKzG4z4iQ/edit?resourcekey=&gid=1270983244#gid=1270983244


@st.cache_data
def carregar_dados():
    sheet_id = "1Ez2ADJrTNzE2tCmlNpoGUsG29PtMVPDP1ZsKzG4z4iQ"
    gid = "1270983244"
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

if st.button("🔄 Atualizar Dados"):
    carregar_dados.clear()
    st.rerun()

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

# Aplicar filtro
df_filtrado = df[
    (df["Dia"] >= pd.to_datetime(data_inicio)) &
    (df["Dia"] <= pd.to_datetime(data_fim))
]

col1, col2, col3 = st.columns(3)

col1.metric(
    "Receita Total",
    f"R$ {df_filtrado['Valor Serviço'].sum():,.2f}"
)

col2.metric(
    "Quantidade de Serviços",
    df_filtrado.shape[0]
)

col3.metric(
    "Ticket Médio",
    f"R$ {(df_filtrado['Valor Serviço'].mean()):,.2f}"
)





st.dataframe(df_filtrado)



