import pandas as pd
import streamlit as st

st.title("Serviços MA 🌴")

# =========================
# 🔄 CARREGAR DADOS
# =========================


@st.cache_data
def carregar_servicos():
    try:
        sheet_id = "1nT6I4SC7eMo8Oowk4g4ypLfHRQhSJeIIcbHXttZ1UW0"
        gid = "409250655"

        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

        df = pd.read_csv(url)
        return df

    except Exception as e:
        st.error(f"Erro ao carregar serviços: {e}")
        return pd.DataFrame()


df_servicos = carregar_servicos()

# =========================
# 🧹 LIMPEZA
# =========================

df_servicos = df_servicos.drop(
    columns=['Carimbo de data/hora'], errors="ignore")

# converter datas
df_servicos["Data"] = pd.to_datetime(df_servicos["Data"], errors="coerce")

# Convertendo horas
df_servicos["Hora Inicial"] = pd.to_datetime(
    df_servicos["Hora Inicial"], errors="coerce")
df_servicos["Hora Final"] = pd.to_datetime(
    df_servicos["Hora Final"], errors="coerce")

df_servicos["Hora Diff"] = (
    df_servicos["Hora Final"] - df_servicos["Hora Inicial"]
).dt.total_seconds() / 3600


# padronizar veículos
df_servicos["Veiculo"] = df_servicos["Veiculo"].astype(
    str).str.replace("-", " ")

# convertendo colunas em inteiras ou decimais
df_servicos["R$ Serviço"] = pd.to_numeric(
    df_servicos["R$ Serviço"], errors='coerce')
df_servicos["R$ Combustivel"] = pd.to_numeric(
    df_servicos["R$ Combustivel"], errors='coerce')
df_servicos["R$ Hospedagem"] = pd.to_numeric(
    df_servicos["R$ Hospedagem"], errors='coerce')
df_servicos["R$ Alimentação"] = pd.to_numeric(
    df_servicos["R$ Alimentação"], errors='coerce')
df_servicos["Pagamento Motorista"] = pd.to_numeric(
    df_servicos["Pagamento Motorista"], errors='coerce')
df_servicos["Km Diff"] = pd.to_numeric(
    df_servicos["Km Diff"], errors='coerce')
df_servicos["Hora Diff"] = pd.to_numeric(
    df_servicos["Hora Diff"], errors='coerce')


df_servicos["R$ Lucro"] = ((
    df_servicos["R$ Serviço"]+df_servicos["R$ Combustivel"] +
    df_servicos["R$ Hospedagem"] + df_servicos["R$ Alimentação"]
)-df_servicos["Pagamento Motorista"])

# =========================
# 🎛️ FILTROS
# =========================

st.sidebar.header("Filtros")

data_inicio = st.sidebar.date_input("Data inicial", df_servicos["Data"].min())
data_fim = st.sidebar.date_input("Data final", df_servicos["Data"].max())

tipos = df_servicos["Tipo Serviço"].dropna().unique()
filtro_tipo = st.sidebar.multiselect(
    "Tipo de Serviço", options=tipos, default=tipos)

motoristas = df_servicos["Motorista"].dropna().unique()
filtro_motorista = st.sidebar.multiselect(
    "Motorista", options=motoristas, default=motoristas)

# aplicar filtros serviços
df_servicos_f = df_servicos[
    (df_servicos["Data"] >= pd.to_datetime(data_inicio)) &
    (df_servicos["Data"] <= pd.to_datetime(data_fim)) &
    (df_servicos["Tipo Serviço"].isin(filtro_tipo) &
     (df_servicos["Motorista"].isin(filtro_motorista)))
]


st.dataframe(df_servicos_f)


if st.button("🔄 Atualizar Dados"):
    carregar_servicos.clear()
    st.rerun()


# =========================
# 📊 KPIs OPERACIONAIS
# =========================

st.markdown("### 🦾 KPIs Operacionais")

col1, col2, col3, col4 = st.columns(4)

total_servicos = len(df_servicos_f)

km_total = df_servicos_f["Km Diff"].sum()

horas_total = df_servicos_f["Hora Diff"].sum()

km_medio = km_total / total_servicos if total_servicos > 0 else 0

col1.metric("Total de Serviços", total_servicos)
col2.metric("KM Rodados", f"{km_total:,.0f} km")
col3.metric("Horas Trabalhadas", f"{horas_total:,.1f}")
col4.metric("KM Médio por Serviço", f"{km_medio:,.1f}")

# =========================
# 🚗 KM POR VEÍCULO
# =========================

st.markdown("### 🚗 KM por Veículo")

km_veiculo = (
    df_servicos_f.groupby("Veiculo")["Km Diff"]
    .sum()
    .sort_values(ascending=False)
)

st.bar_chart(km_veiculo)


# =========================
# 💰 KPIs FINANCEIROS
# =========================

st.markdown("### 📊 KPIs Financeiros")

col1, col2, col3 = st.columns(3)

receita_total = df_servicos_f["R$ Serviço"].sum()
despesa_total = df_servicos_f["Pagamento Motorista"].sum()
lucro_total = receita_total - despesa_total

col1.metric("Receita Total", f"R$ {receita_total:,.2f}")
col2.metric("Despesas Totais", f"R$ {despesa_total:,.2f}")
col3.metric("Lucro Total", f"R$ {lucro_total:,.2f}")

# =========================
# 📈 SERVIÇOS POR DIA
# =========================

st.markdown("### 📈 Serviços por Dia")

servicos_por_dia = (
    df_servicos_f.groupby(["Data", "Tipo Serviço"])
    .size()
    .unstack(fill_value=0)
)

st.bar_chart(servicos_por_dia)

# =========================
# 🏆 RANKING MOTORISTAS
# =========================

st.markdown("### 🏆 Ranking de Motoristas")

ranking_motoristas = (
    df_servicos_f.groupby("Motorista")
    .size()
    .reset_index(name="Quantidade")
    .sort_values(by="Quantidade", ascending=False)
)

st.dataframe(ranking_motoristas)
st.bar_chart(ranking_motoristas.set_index("Motorista"))

# =========================
# 🚗 RESULTADO POR VEÍCULO
# =========================

st.markdown("### 🚗 Resultado por Veículo")

# serviços
servicos_agg = df_servicos_f.groupby("Veiculo").agg({
    "Valor Serviço MF": "sum",
    "Km Diff": "sum"
}).reset_index()

# despesas
despesas_agg = df_despesas_f.groupby(
    "Veiculo")["Valor Despesa"].sum().reset_index()

# merge
df_final = pd.merge(servicos_agg, despesas_agg, on="Veiculo", how="left")

df_final["Valor Despesa"] = df_final["Valor Despesa"].fillna(0)

# métricas
df_final["Lucro"] = df_final["Valor Serviço MF"] - df_final["Valor Despesa"]

df_final["Custo por Km"] = df_final["Valor Despesa"] / df_final["Km Diff"]
df_final["Custo por Km"] = df_final["Custo por Km"].replace([float("inf")], 0)

# formatação
df_final_formatado = df_final.copy()

df_final_formatado["Valor Serviço MF"] = df_final_formatado["Valor Serviço MF"].map(
    "R$ {:,.2f}".format)
df_final_formatado["Valor Despesa"] = df_final_formatado["Valor Despesa"].map(
    "R$ {:,.2f}".format)
df_final_formatado["Lucro"] = df_final_formatado["Lucro"].map(
    "R$ {:,.2f}".format)
df_final_formatado["Custo por Km"] = df_final_formatado["Custo por Km"].map(
    "R$ {:,.2f}".format)

# tabela
st.dataframe(df_final_formatado)

# gráfico lucro
st.markdown("### 💰 Lucro por Veículo")

st.bar_chart(df_final.set_index("Veiculo")["Lucro"])
