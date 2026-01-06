import streamlit as st
import pandas as pd

#  CONFIGURAÇÃO DA PÁGINA
st.set_page_config(layout="wide", page_title="🎬 Filmes")
st.title("🎬 Dashboard de Filmes ")

#  CARREGAMENTO DOS DADOS
arquivo = st.file_uploader("Carregue o arquivo filmes.csv", type="csv")

if arquivo is not None:
    try:
        # Lê o arquivo corrigindo o separador (;)
        df = pd.read_csv(arquivo, sep=';', encoding='utf-8', on_bad_lines='skip')

        # LIMPEZA E TRATAMENTO 
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
        df['Ano'] = df['release_date'].astype(str).str.extract(r'(\d{4})')
        df = df.dropna(subset=['rating', 'Ano'])
        df = df[df['genres'] != 'sem genres']
        df = df[df['countries_origin'] != 'sem countries']

        #  FILTROS (SIDEBAR)
        st.sidebar.header("Filtros")
        
        opcoes_generos = sorted(df['genres'].unique())
        
        generos_selecionados = st.sidebar.multiselect(
            "Filtrar por Gênero:", 
            options=opcoes_generos,
            placeholder="Selecione gêneros (Vazio = Todos)"
        )

        # APLICANDO O FILTRO 
        if not generos_selecionados:
            df_filtrado = df
            texto_filtro = " Filmes "
        else:
            df_filtrado = df[df['genres'].isin(generos_selecionados)]
            texto_filtro = ", ".join(generos_selecionados)

        #  DASHBOARD VISUAL
        st.subheader(f"Análise Atual: {texto_filtro}")

        # CARTÕES (KPIs)
        total = len(df_filtrado)
        media = df_filtrado['rating'].mean()
        
        if total > 0:
            top_pais = df_filtrado['countries_origin'].mode()[0]
        else:
            top_pais = "-"
            media = 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Total de Filmes", f"{total:,.0f}")
        c2.metric("Média de Notas", f"{media:.1f}")
        c3.metric("País Principal", top_pais)

        st.divider()

        # GRÁFICOS LADO A LADO
        g1, g2 = st.columns(2)

        with g1:
            st.caption("🏆 Top 5 Países de Origem")
            contagem_paises = df_filtrado['countries_origin'].value_counts().head(5)
          
            st.bar_chart(contagem_paises, color="#FF4B4B")

        with g2:
            st.caption("📅 Evolução de Lançamentos por Ano")
            contagem_anos = df_filtrado['Ano'].value_counts().sort_index()
            
        
            st.line_chart(contagem_anos, color="#FF4B4B")

      
        st.divider()
        
        with st.expander("📋 Dados Brutos"):
            st.write("Aqui estão todos os detalhes dos filmes filtrados:")
            st.dataframe(df_filtrado, use_container_width=True, hide_index= True)
            
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")

else:
    st.info("Aguardando upload do arquivo CSV...")