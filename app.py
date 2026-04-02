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
from etl_preprocessor import run_full_etl, get_google_sheet_data
from etl_utils import DataProcess, FilterSelection, dre
from charts import (
    config_plot,
    plot_hist,
    plot_hztl,
    plot_pie,
    create_table,
    PainelEventos,
    GeradorRelatoriosEventos,
)

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
warnings.filterwarnings("ignore")  # Ignora warnings para uma execução mais limpa

# Configuração de temas para Plotly
pio.templates.default = "plotly_white"

# Configurações padrão para Plotly Express
px.defaults.template = "plotly_white"
px.defaults.color_continuous_scale = px.colors.sequential.Blackbody
px.defaults.width = 1024
px.defaults.height = 768

# # Configuração de localização para formatação de números e datas (Ex: R$ 1.000,00)
# try:
#     locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
# except locale.Error:
#     # Fallback to a common, system-available locale that supports UTF-8
#     # C.UTF-8 is often available in modern environments
#     try:
#         locale.setlocale(locale.LC_ALL, "C.UTF-8")
#     except locale.Error:
#         # Final fallback - usually "C" which is guaranteed to work but lacks UTF-8 support
#         locale.setlocale(locale.LC_ALL, "C")

# 2. Configuração da Página Streamlit
# -----------------------------------------------------------------------------

st.set_page_config(layout="wide")
st.title("Análise e Gestão de Eventos 📊")

# 3. Processamento de Dados (ETL e Pré-processamento)
# -----------------------------------------------------------------------------

# Determina a data e o ano atual para uso nos filtros
currentDate = date.today()
currentYear = currentDate.year

#@st.cache_data
def load_data():
    try:
        df = run_full_etl(
            sheet_title="Prog_eventos_thai_house",
            worksheet_name="Completa",
            local=False
        )
    except:
        df = run_full_etl(
            sheet_title="Prog_eventos_thai_house",
            worksheet_name="Completa",
            local=True
        )
    return df

# Carrega os dados
df_load = load_data()

# df_load = get_google_sheet_data(sheet_title= "Prog_eventos_thai_house", worksheet_name="Completa", local=False)

st.dataframe(df_load)

# df_old = get_google_sheet_data(sheet_title="dados_anos_anteriores", worksheet_name="Sheet1", local=False)

# st.dataframe(df_old)
