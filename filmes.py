import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Apex Cinema", page_icon="🎬", layout="wide")

st.title("🎬 Apex Cinema")
st.caption("Fonte: IMDb | 1960 - 2024")

# 01- fazendo o upload do csv
arquivo = st.file_uploader("Faça o upload do arquivo CSV", type=["csv"])

if arquivo is None:
    st.info("Aguardando upload do arquivo CSV para exibir os gráficos.")
    st.stop()

# 02 - carregando os dados do csv
@st.cache_data
def load_data(file):
    df = pd.read_csv(file, sep=";", encoding="utf-8-sig")

    # 03 - renomeando as colunas
    colunas = ["Titulo", "Ano", "Nota", "Genero", "Pais", "Idioma"]
    for i in range(len(df.columns) - 6):
        colunas.append("Extra" + str(i))
    df.columns = colunas

    df = df[["Titulo", "Ano", "Nota", "Genero", "Pais", "Idioma"]]

    # 04 - arrumando a coluna nota (estava com virgula)
    df["Nota"] = df["Nota"].astype(str)
    df["Nota"] = df["Nota"].str.replace(",", ".")
    df["Nota"] = df["Nota"].str.strip()
    df["Nota"] = pd.to_numeric(df["Nota"], errors="coerce")

    # 05 - arrumando a coluna ano
    df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce")
    df = df.dropna(subset=["Ano"])
    df = df[df["Ano"] != float("inf")]
    df["Ano"] = df["Ano"].astype(int)

    return df

df = load_data(arquivo)

# 06 - filtros na barra lateral
st.sidebar.header("Filtros")

ano_min = int(df["Ano"].min())
ano_max = int(df["Ano"].max())
ano_range = st.sidebar.slider("Ano", min_value=ano_min, max_value=ano_max, value=(ano_min, ano_max))

# 07 - pegando todos os generos unicos
lista_generos = []
for generos in df["Genero"].dropna():
    for g in generos.split(","):
        g = g.strip()
        if g not in lista_generos:
            lista_generos.append(g)
lista_generos = sorted(lista_generos)
genero_sel = st.sidebar.selectbox("Gênero", ["Todos"] + lista_generos)

# 08 - pegando todos os paises unicos
lista_paises = []
for paises in df["Pais"].dropna():
    for p in paises.split(","):
        p = p.strip()
        if p not in lista_paises:
            lista_paises.append(p)
lista_paises = sorted(lista_paises)
pais_sel = st.sidebar.selectbox("País", ["Todos"] + lista_paises)

nota_sel = st.sidebar.selectbox("Nota mínima", ["Todos", "6+", "7+", "8+"])

# 09 - aplicando os filtros
filtrado = df[(df["Ano"] >= ano_range[0]) & (df["Ano"] <= ano_range[1])]

if genero_sel != "Todos":
    filtrado = filtrado[filtrado["Genero"].str.contains(genero_sel, na=False)]

if pais_sel != "Todos":
    filtrado = filtrado[filtrado["Pais"].str.contains(pais_sel, na=False)]

if nota_sel != "Todos":
    nota_minima = float(nota_sel.replace("+", ""))
    filtrado = filtrado[filtrado["Nota"] >= nota_minima]

# 10 - mostrando os graficos
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 Gêneros")
    if not filtrado.empty:
        generos_explodidos = filtrado["Genero"].dropna().str.split(",").explode().str.strip()
        contagem_generos = generos_explodidos.value_counts().head(10).reset_index()
        contagem_generos.columns = ["Gênero", "Quantidade"]

        fig1 = px.bar(contagem_generos, x="Quantidade", y="Gênero", orientation="h",
                      color_discrete_sequence=["#4C9BE8"])
        fig1.update_layout(yaxis=dict(autorange="reversed"), height=380,
                           margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Top 10 Países")
    if not filtrado.empty:
        paises_explodidos = filtrado["Pais"].dropna().str.split(",").explode().str.strip()
        contagem_paises = paises_explodidos.value_counts().head(10).reset_index()
        contagem_paises.columns = ["País", "Quantidade"]

        fig2 = px.bar(contagem_paises, x="Quantidade", y="País", orientation="h",
                      color_discrete_sequence=["#A78BFA"])
        fig2.update_layout(yaxis=dict(autorange="reversed"), height=380,
                           margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig2, use_container_width=True)

st.subheader("Filmes por Ano")
if not filtrado.empty:
    filmes_por_ano = filtrado.groupby("Ano").size().reset_index(name="Quantidade")

    fig3 = px.line(filmes_por_ano, x="Ano", y="Quantidade", markers=True,
                   color_discrete_sequence=["#34D399"])
    fig3.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig3, use_container_width=True)