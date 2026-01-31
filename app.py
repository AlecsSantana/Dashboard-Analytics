import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊",
    layout="wide", 
)


st.markdown("""
    <style>
    /* Cor de fundo da barra lateral */
    [data-testid="stSidebar"] {
        background-color: #0000;
    }
    /* Cor das tags selecionadas no multiselect */
    span[data-baseweb="tag"] {
        background-color: #6A0DAD !important;
    }
    /* Cor da borda e interações dos inputs */
    div[data-baseweb="select"] > div {
        border-color: #6A0DAD !important;
    }
    /* Títulos da barra lateral */
    [data-testid="stSidebar"] h2 {
        color: #6A0DAD;
    }
    </style>
    """, unsafe_allow_html=True)


@st.cache_data
def load_data():
    return pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")

df = load_data()


st.sidebar.header(" Filtros")

anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

senioridades_disponiveis = sorted(df['senioridade'].unique())
senioridades_selecionadas = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)

contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", contratos_disponiveis, default=contratos_disponiveis)

tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)

# --- Filtragem ---
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

# --- Conteúdo Principal ---
st.title("🎲 Dashboard de Análise de Salários na Área de Dados")
st.markdown("Explore os dados salariais utilizando os filtros roxos à esquerda.")


if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Salário médio", f"${salario_medio:,.0f}")
    col2.metric("Salário máximo", f"${salario_maximo:,.0f}")
    col3.metric("Total de registros", f"{total_registros:,}")
    col4.metric("Cargo mais frequente", cargo_mais_frequente)

st.markdown("---")


st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos, x='usd', y='cargo', orientation='h',
            title="Top 10 cargos por salário médio",
            color_discrete_sequence=["#0DE889"] 
        )
        st.plotly_chart(grafico_cargos, use_container_width=True)

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado, x='usd', nbins=30,
            title="Distribuição de salários anuais",
            color_discrete_sequence=["#07468F"] 
        )
        st.plotly_chart(grafico_hist, use_container_width=True)

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem, names='tipo_trabalho', values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5,
            color_discrete_sequence=["#ECD20D", "#66A4F0", "#FF0000"]
        )
        st.plotly_chart(grafico_remoto, use_container_width=True)

with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(
            media_ds_pais, locations='residencia_iso3', color='usd',
            color_continuous_scale='blues',
            title='Média salarial (DS) por país'
        )
        st.plotly_chart(grafico_paises, use_container_width=True)

st.subheader("Dados Detalhados")

st.dataframe(df_filtrado)
#by:alecs
