from __future__ import print_function
from datetime import datetime as dt

import locale
import numpy as np
import pandas as pd
import warnings
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

try:
    from arq_py.mod_func import colunas_lower_replace, whitespace_remover  # Funções auxiliares (biblioteca local)
except:
    from mod_func import colunas_lower_replace, whitespace_remover 

warnings.filterwarnings("ignore")



# -------------------------------------------------------------------------
# FUNÇÃO DE EXTRAÇÃO DE DADOS (E do ETL) - USO EXCLUSIVO DO STREAMLIT CLOUD
# -------------------------------------------------------------------------
# O cache evita que a planilha seja lida novamente a cada interação do usuário.
#@st.cache_data(ttl=600) # ttl=600 significa que o cache dura 10 minutos
def get_google_sheet_data(sheet_title: str, worksheet_name: str, local: bool = False) -> pd.DataFrame:

    if not local:

        """
        Autentica no Google Sheets usando st.secrets e carrega o DataFrame.
        """

        gcp_service_account = st.secrets["gcp_service_account"]
        
        # 1. Carrega as credenciais do Streamlit Secrets 
        # (Nome da chave deve ser o mesmo usado no seu .streamlit/secrets.toml)
        try:
            gcp_service_account_dict = dict(st.secrets["gcp_service_account"])
        except FileNotFoundError:
            st.error("Erro: O arquivo .streamlit/secrets.toml não foi configurado.")
            return pd.DataFrame()
            
        # 2. Autentica o gspread
        gc = gspread.service_account_from_dict(gcp_service_account_dict)
        
        # 3. Abre a planilha e a aba
        # ATENÇÃO: Substitua os placeholders pelos nomes reais da sua planilha e aba!
        sh = gc.open(sheet_title)
        worksheet = sh.worksheet(worksheet_name)
        
        # 4. Obtém todos os dados (lista de listas)
        data = worksheet.get_all_values()
        
        # 5. Cria o DataFrame (primeira linha como cabeçalho, resto como dados)
        df = pd.DataFrame(data[1:], columns=data[0])
        
        print(f'Dados carregados de: {sheet_title} - {worksheet_name}')
        return df
    
    else:
          
        """
        Autentica no Google Sheets e carrega o DataFrame.
        """
        service_account = '/home/rb/Dropbox/thai_house/thai/cred/credential_thai.json'

        # 2. Autentica o gspread LENDO DIRETAMENTE DO ARQUIVO
        try:
            gc = gspread.service_account(filename=service_account) 
        except FileNotFoundError:
            # Use um print simples ou raise/logging, já que st.error só funciona no ambiente Streamlit
            print(f"Erro: O arquivo de credenciais não foi encontrado em {service_account}")
            return pd.DataFrame()
        except Exception as e:
            print(f"Erro ao autenticar com gspread: {e}")
            return pd.DataFrame()
        
        # 3. Abre a planilha e a aba
        # ATENÇÃO: Substitua os placeholders pelos nomes reais da sua planilha e aba!
        sh = gc.open(sheet_title)
        worksheet = sh.worksheet(worksheet_name)
        
        # 4. Obtém todos os dados (lista de listas)
        data = worksheet.get_all_values()
        
        # 5. Cria o DataFrame (primeira linha como cabeçalho, resto como dados)
        df = pd.DataFrame(data[1:], columns=data[0])
        
        print(f'Dados carregados de: {sheet_title} - {worksheet_name}')
        return df


# -------------------------------------------------------------------------
# FUNÇÃO PRINCIPAL DE ETL (T e L)
# -------------------------------------------------------------------------

def format_cols(df: pd.DataFrame, columns_int: list = None, columns_float: list = None, columns_date: list = None):
    # if not columns_int:
    #     columns_int = [
    #         "kids_presentes",
    #         "kids",
    #         "convidados_presentes",
    #         "convidados_previstos",
    #         "total_convidados_previsto",
    #         "total_convidados_presentes",
    #     ]
    
    # if not columns_float:
    #     columns_float = [
    #         "sinal",
    #         "preço_kids",
    #         "valor_extra",
    #         "preço",
    #         "valor_total_previsto",
    #         "valor_total_realizado",
    #     ]

    # if not columns_date:
    #     columns_date = ["data_contato", "data_evento"]

    df[columns_int] = df[columns_int].astype(float).astype("uint16")
    df[columns_float] = df[columns_float].astype("float32").round()
    df[columns_date] = df[columns_date].apply(
        lambda x: pd.to_datetime(x, errors="coerce", dayfirst=True)
    )
    return df


def run_full_etl(sheet_title: str = None, worksheet_name: str = None, local: bool = False) -> pd.DataFrame:
    """
    Executa a sequência completa de Extração, Transformação e Carregamento (ETL).
    
    :param sheet_title: Título da planilha no Google Sheets.
    :param worksheet_name: Nome da aba/worksheet dentro da planilha.
    :returns: O DataFrame processado final.
    """

    # Informa o local para formatação de data e moeda
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

    # Configura o Pandas
    pd.set_option("display.precision", 2)
    pd.set_option("display.max_columns", None)


    # 1. EXTRAÇÃO (E): CHAMADA DA FUNÇÃO DE CONEXÃO
    # A variável df_completo recebe os dados do Google Sheets
    try:
        X = get_google_sheet_data(sheet_title, worksheet_name, local=True)
    except:
        X = get_google_sheet_data(sheet_title, worksheet_name, local=False)

    columns_int = [
        "convidados_previstos",
        "kids",
        "convidados_presentes",
        "kids_presentes",
        "total_convidados_previsto",
        "total_convidados_presentes",
    ]
    columns_string = [
        "local",
        "etapa",
        "tipo",
        "cardápio",
        "manter_total_previsto",
        "data_evento",
    ]
    columns_float= list(set(X.columns.tolist()) - set(columns_int) - set(columns_string))

    return format_cols(X, 
                       columns_int=columns_int,
                       columns_float=columns_float,
                       columns_date='data_evento')

if __name__ == "__main__":
    print('Iniciando processamento.....')
    df = run_full_etl(
    sheet_title="dados_siteThai", worksheet_name="df_site", local=True
)

    print(df.info())

