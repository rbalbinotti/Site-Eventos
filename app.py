# bibliotecas
import locale
import warnings
import pandas as pd
import numpy as np
import streamlit as st

from datetime import date
from dateutil.relativedelta import relativedelta

# Importações de módulos locais (presume-se que existam)
# ATENÇÃO: Essas importações são mantidas, mas as classes/funções
# etl_preprocessor, etl_utils, charts DEVE EXISTIR para o código rodar.
from etl_preprocessor import run_full_etl
from etl_utils import DataProcess, FilterSelection, dre
from charts import config_plot, plot_hist, plot_hztl, plot_pie, create_table, PainelEventos, GeradorRelatoriosEventos

# Gráficos
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

# 1. Configurações Iniciais
# -----------------------------------------------------------------------------

# Configuração pandas
# Define opções de visualização para DataFrames
pd.set_option("display.precision", 2)
pd.set_option("display.max_columns", 30)
warnings.filterwarnings("ignore") # Ignora warnings para uma execução mais limpa

# Configuração de temas para Plotly
pio.templates.default = "plotly_white"

# Configurações padrão para Plotly Express
px.defaults.template = "plotly_white"
px.defaults.color_continuous_scale = px.colors.sequential.Blackbody
px.defaults.width = 1024
px.defaults.height = 768

# Configuração de localização para formatação de números e datas (Ex: R$ 1.000,00)
try:
    locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
except locale.Error:
    # Fallback to a common, system-available locale that supports UTF-8
    # C.UTF-8 is often available in modern environments
    try:
        locale.setlocale(locale.LC_ALL, "C.UTF-8")
    except locale.Error:
        # Final fallback - usually "C" which is guaranteed to work but lacks UTF-8 support
        locale.setlocale(locale.LC_ALL, "C")

# 2. Configuração da Página Streamlit
# -----------------------------------------------------------------------------

st.set_page_config(layout="wide")
st.title("Análise e Gestão de Eventos 📊") 

# 3. Processamento de Dados (ETL e Pré-processamento)
# -----------------------------------------------------------------------------

# Determina a data e o ano atual para uso nos filtros
currentDate = date.today()
currentYear = currentDate.year


try:
    @st.cache_data
    def load_data():
        """Roda o processo completo de ETL e carrega os dados brutos."""
        df = run_full_etl(sheet_title="Prog_eventos_thai_house", worksheet_name="Completa", local=False)
        return df
except:
    @st.cache_data
    def load_data():
        """Roda o processo completo de ETL e carrega os dados brutos."""
        df = run_full_etl(sheet_title="Prog_eventos_thai_house", worksheet_name="Completa", local=True)
        return df
    
# Carrega os dados
df_load = load_data()

# Pré-processamento e filtragem inicial
preprocessor = DataProcess()
# Processa e filtra dados para incluir apenas eventos a partir de 2022 (Ano > 2021)
df = preprocessor.process_data(df_load).query('`Ano evento` > 2021') 

# 4. Barra Lateral e Configurações de Filtro
# -----------------------------------------------------------------------------

# Cria listas únicas para as opções de filtro
local_list = df['Local'].unique().tolist()
etapa_list = df['Etapa'].unique().tolist()
ano_list = df['Ano evento'].unique().tolist()
mes_list = df['Mes evento'].unique().tolist()

st.sidebar.header('Filtros de Análise', divider='gray')

# --- Caixas de seleção ---

# Seleção de Local
place_select = st.sidebar.multiselect(
    "Selecione o(s) Local(is) para Análise:", 
    local_list, 
    default=local_list
)

# Formatação do nome do local para exibição no título
if len(place_select) > 1:
    place_select_formated = " / ".join(place_select)
else:
    place_select_formated = "".join(place_select)

# Seleção de Ano
year_select = st.sidebar.selectbox(
    "Selecione o Ano para Análise:",
    sorted(ano_list, reverse=True),
    # Define o ano atual como padrão, se estiver na lista
    index=sorted(ano_list, reverse=True).index(currentYear) if currentYear in ano_list else 0
)

# Seleção de Etapa
stage_select = st.sidebar.multiselect(
    'Selecione a(s) Etapa(s) do Evento:', 
    etapa_list, 
    default=etapa_list
)

# Inicialização das classes de filtro
filter_class = FilterSelection(place_select, stage_select, year_select)
# Filtros específicos para locais (usados nas tabelas de estatísticas)
filter_thai = FilterSelection(place_select=['Thai house'], stage_select=etapa_list, year_select=year_select)
filter_river = FilterSelection(place_select=['River'], stage_select=etapa_list, year_select=year_select)


# 5. Estrutura Principal do Dashboard com Abas
# -----------------------------------------------------------------------------

# Modificação: Adição da aba de Conversão e renomeação da aba Consolidado
tab_financ, tab_demanda, tab_detalhes, tab_executivo = st.tabs([
    "💰 Visão Financeira", # Título simplificado
    "📈 Análise de Demanda & Frequência", 
    "📋 Detalhamento & Estatísticas",
    "Relatórios Executivos (KPIs)" # ABA CONSOLIDADO RENOMEADA
])

# -----------------------------------------------------------------------------
# ABA 1: Visão Financeira
# -----------------------------------------------------------------------------
with tab_financ:
    st.subheader('Evolução Histórica de Valores', divider='gray')
    st.write(f'Análise da evolução dos valores ao longo do tempo (acumulado por ano).')

    col1, col2 = st.columns(2)

    # Gráfico: Valor Previsto Acumulado por Ano
    with col1:
        st.write(f'Valor Total Previsto (Acumulado por Ano)')
        plot_ = config_plot(
            plot_hist(
                df, 
                x_axis='Ano evento',
                y_axis='Valor total previsto',
                color='Local')
            , legend = False, ord_date=True)
        st.plotly_chart(plot_, width='stretch') # Adicionado use_container_width

    # Gráfico: Valor Realizado Acumulado por Ano
    with col2:
        st.write(f'Valor Total Realizado (Acumulado por Ano)')
        plot_ = config_plot(
            plot_hist(
                df, 
                x_axis='Ano evento',
                y_axis='Valor total realizado',
                color='Local')
            , legend = True, ord_date=True)
        st.plotly_chart(plot_, width='stretch') # Adicionado use_container_width
    
    st.subheader(f'Desempenho Mensal em {year_select} - {place_select_formated}', divider='gray')
    col1b, col2b = st.columns(2)

    # Gráfico: Valor Previsto Mensal (Ano Selecionado)
    with col1b:
        st.write(f'Valor Previsto Mensal')
        plot_ = config_plot(
            plot_hist(
                filter_class.run_filter(df), 
                x_axis='Mes evento',
                y_axis='Valor total previsto',
                color='Local')
            , legend = False, ord_date=True)
        st.plotly_chart(plot_, width='stretch') # Adicionado use_container_width

    # Gráfico: Valor Realizado Mensal (Ano Selecionado)
    with col2b:
        st.write(f'Valor Realizado Mensal')
        plot_ = config_plot(
            plot_hist(
                filter_class.run_filter(df), 
                x_axis='Mes evento',
                y_axis='Valor total realizado',
                color='Local')
            , legend = True, ord_date=True)
        st.plotly_chart(plot_, width='stretch') # Adicionado use_container_width

    with col1b:
        # Gráfico: Ticket Médio (Agora em largura total para destaque)
        st.subheader(f"Ticket Médio por Local", divider='gray')

        # Altere de st.columns([1, 1]) para não usar colunas aqui, ou usar colunas para 
        # ter espaço para outro KPI importante, como Margem. Aqui usarei largura total.
        # col_tm, _ = st.columns([1, 1]) # Removido para largura total

        # with col_tm: # Removido para largura total
        
        # Calcula o Ticket Médio: Valor Total Realizado / Total Convidados Presentes
        dfg = df.query('Etapa == "Realizado"').groupby(['Local', 'Ano evento'])[['Total convidados presentes', 'Valor total realizado']].sum().reset_index()
        dfg['Ticket médio'] = dfg['Valor total realizado'] / dfg['Total convidados presentes']

        plot_ = config_plot(
            plot_hist(
                filter_class.run_filter(dfg, filter_stage=False),
                x_axis='Ano evento',
                y_axis='Ticket médio',
                color='Local')
                , ord_date=False, legend=True)
        st.plotly_chart(plot_, width='stretch') # Adicionado use_container_width


# -----------------------------------------------------------------------------
# ABA 2: Análise de Demanda & Frequência
# -----------------------------------------------------------------------------
with tab_demanda:
    st.subheader('Volume de Procura (Orçamentos e Convidados)', divider='gray')
    
    # Colunas para Frequência de Orçamentos
    col_e, col_c = st.columns(2) # Modificado de 3 para 2 para otimizar espaço

    with col_e:
        st.write('Frequência de Orçamentos por Ano')
        # Cria o histograma
        figh = px.histogram(
            df[["Ano evento", "Local"]],
            y="Ano evento",
            color="Local",
            title="",
            text_auto=True,
        )
        # Configurações do layout
        figh.update_layout(title='', bargap=0.1, separators=",.", showlegend=False)
        figh.update_yaxes(title=None, dtick=1)
        figh.update_xaxes(title=None)
        st.plotly_chart(figh, width='stretch') # Mantido width='stretch'

    with col_c:
        st.write(f"Orçamentos Solicitados por Mês em {year_select}")
        plotted = config_plot(
            plot_hist(filter_class.run_filter(df), 'Mes evento'),
            ord_date=True,
            legend='Local')
        st.plotly_chart(plotted, width='stretch') # Adicionado use_container_width

    col_convidados_ano, col_convidados_mes = st.columns(2)

    with col_convidados_ano:
        st.write(f"Total de Convidados (Previsto/Realizado) por Ano") # Título mais claro
        st.caption('Nota: Considera-se o total de convidados presentes em eventos realizados a partir de 2025.') # Texto atualizado
        plot_ = plot_hztl(df, select_month=False)
        st.plotly_chart(plot_, width='stretch')

    with col_convidados_mes:
        st.write(f"Total de Convidados (Previsto/Realizado) por Mês") # Título mais claro
        st.caption('Nota: Considera-se o total de convidados presentes em eventos realizados a partir de 2025.') # Texto atualizado
        plot_ = plot_hztl(df, select_month=True)
        st.plotly_chart(plot_, width='stretch')

    st.subheader('Distribuição da Procura (Gráficos de Pizza)', divider='gray')
    
    # Gráficos de Pizza: Mês e Dia da Semana
    col_pie1, col_pie2 = st.columns(2)

    with col_pie1:
        st.write(f"Distribuição de Orçamentos por Mês - Ano {year_select}")
        fig_pie = plot_pie(filter_class.run_filter(df), 'Mes evento')
        st.plotly_chart(fig_pie, width='stretch')

    with col_pie2:
        st.write(f"Distribuição por Dia da Semana - Ano {year_select}")
        fig_pie = plot_pie(filter_class.run_filter(df), 'Dia semana')
        st.plotly_chart(fig_pie, width='stretch')

    # Gráficos de Pizza: Etapa e Cardápio
    col_pie3, col_pie4 = st.columns(2)

    with col_pie3:
        st.write(f"Status do Processo (Etapas) - Ano {year_select}")
        fig_pie = plot_pie(filter_class.run_filter(df), 'Etapa')
        st.plotly_chart(fig_pie, width='stretch')

    with col_pie4:
        st.write(f"Procura por Tipo de Cardápio - Ano {year_select}")
        fig_pie = plot_pie(filter_class.run_filter(df), 'Cardápio')
        st.plotly_chart(fig_pie, width='stretch')

# # -----------------------------------------------------------------------------
# # ABA 3: Funil & Taxas de Conversão (Nova Aba)
# # -----------------------------------------------------------------------------
# with tab_conversao:
#     st.subheader('Análise do Funil de Vendas e Conversão', divider='gray')
#     st.info('Esta seção requer a definição das métricas de funil na classe `etl_utils` ou a criação de funções de cálculo de conversão.')

#     # Estrutura para Funil de Eventos (Exemplo de Funil)
#     col_funil, col_taxas = st.columns(2)
    
#     with col_funil:
#         st.write("Funil de Etapas de Eventos (Orçamento > Negociação > Fechado)")
#         # Simulação de um gráfico de Funil (necessita de função 'plot_funnel' real)
#         # fig_funil = plot_funnel(filter_class.run_filter(df))
#         # st.plotly_chart(fig_funil, width='stretch')
#         st.markdown("> **Placeholder:** Gráfico de Funil (Volume de Eventos por Etapa).")

#     with col_taxas:
#         st.write("Taxas de Conversão Chave")
#         # Simulação de KPIs de Conversão
#         # st.metric("Taxa Orçamento -> Fechado", "X.X%", delta="Y.Y% vs. Mês Anterior")
#         # st.metric("Taxa Fechado -> Realizado", "Z.Z%", delta="W.W% vs. Meta")
#         st.markdown("> **Placeholder:** Cartões de Métricas (KPIs de Conversão).")
#         st.markdown("> **Placeholder:** Desempenho (Valor Realizado / Valor Previsto).")


# -----------------------------------------------------------------------------
# ABA 4: Detalhamento & Estatísticas
# -----------------------------------------------------------------------------
with tab_detalhes:
    # 6. Estatísticas Descritivas por Local
    # -------------------------------------------------------------------------
    # Aplica filtros e calcula estatísticas para Thai House
    filter_thai_real_fech = FilterSelection(place_select=['Thai house'], stage_select=stage_select, year_select=year_select)
    thai_loc = filter_thai_real_fech.run_filter(df, filter_place=True, filter_stage=True, filter_year=True)
    thai_loc = thai_loc.loc[:,["Total convidados previsto", "Valor total previsto",  "Total convidados presentes", "Valor total realizado"]
    ].describe().T

    # Aplica filtros e calcula estatísticas para River
    filter_river_real_fech = FilterSelection(place_select=['River'], stage_select=stage_select, year_select=year_select)
    river_loc = filter_river_real_fech.run_filter(df, filter_place=True, filter_stage=True, filter_year=True)
    river_loc = river_loc.loc[:,["Total convidados previsto", "Valor total previsto",  "Total convidados presentes", "Valor total realizado"]
    ].describe().T
    
    st.subheader(f'Estatísticas Descritivas Agregadas em {year_select}', divider='gray')
    col_stat_thai, col_stat_river = st.columns(2)

    with col_stat_thai:
        st.write(f'Estatísticas Descritivas: Thai House')
        st.dataframe(thai_loc, width='stretch') # Adicionado use_container_width
    
    with col_stat_river:
        st.write(f'Estatísticas Descritivas: River')
        st.dataframe(river_loc, width='stretch') # Adicionado use_container_width
        
    # 7. Tabelas Detalhadas
    # -------------------------------------------------------------------------

    st.subheader(f'Tabelas de Eventos Detalhados por Status em {year_select} ({place_select_formated})', divider='gray')
    st.caption('Observação: Datas no formato Mês/Dia/Ano')

    # Títulos e DataFrames ajustados para consistência
    st.write('Eventos em Negociação (Previsto)')
    df_int = create_table(filter_class.run_filter(df), etapa_select='Negociação', previsto=True)
    st.dataframe(df_int, width='stretch')

    st.write('Eventos Fechados (Previsto)')
    df_int = create_table(filter_class.run_filter(df), etapa_select='Fechado', previsto=True)
    st.dataframe(df_int, width='stretch')

    st.write('Eventos Realizados (Realizado)')
    df_int = create_table(filter_class.run_filter(df), etapa_select='Realizado', previsto=False)
    st.dataframe(df_int, width='stretch')

# -----------------------------------------------------------------------------
# ABA 5: Relatórios Executivos (KPIs)
# -----------------------------------------------------------------------------
with tab_executivo:
    # 8. Painéis de Resumo e Relatórios
    # -------------------------------------------------------------------------
    st.subheader(f'Painéis de Resumo Comparativo por Período', divider='gray')
    
    col_esq, col_dir = st.columns(2)

    with col_esq:
        st.write("Painel de Performance (Último Mês)") # Título mais descritivo
        painel_maker = PainelEventos(n_meses_retroativos=1)
        fig_final = painel_maker.gerar_painel(df)
        st.plotly_chart(fig_final, width='stretch')
    
    with col_dir:
        st.write("Painel de Performance (Últimos 2 Meses)") # Título mais descritivo
        painel_maker = PainelEventos(n_meses_retroativos=2)
        fig_final = painel_maker.gerar_painel(df)
        st.plotly_chart(fig_final, width='stretch')

    st.subheader(f'Relatórios Completos por Local - Eventos Realizados em {year_select}', divider='gray')

    st.caption('Relatórios gerados a partir de 2025.')

    col_esq, col_dir = st.columns(2)

    with col_esq:
        st.write(f"Thai house - Análise Detalhada de Eventos Realizados")
        summary_generator = GeradorRelatoriosEventos(df, ano_referencia=year_select, local_analisado='Thai house')
        summary_plot = summary_generator.gerar_relatorio_completo()
        st.plotly_chart(summary_plot, width='stretch', key='plotly_chart1')
    
    with col_dir:
        st.write(f"River - Análise Detalhada de Eventos Realizados")
        summary_generator = GeradorRelatoriosEventos(df, ano_referencia=year_select, local_analisado='River')
        summary_plot = summary_generator.gerar_relatorio_completo()
        st.plotly_chart(summary_plot, width='stretch', key='plotly_chart2')