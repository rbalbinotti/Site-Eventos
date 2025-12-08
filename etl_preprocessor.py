from __future__ import print_function
from datetime import datetime as dt

import locale
from mod_func import colunas_lower_replace, whitespace_remover  # Funções auxiliares (biblioteca local)
import numpy as np
import pandas as pd
import warnings
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

warnings.filterwarnings("ignore")



# -------------------------------------------------------------------------
# FUNÇÃO DE EXTRAÇÃO DE DADOS (E do ETL) - USO EXCLUSIVO DO STREAMLIT CLOUD
# -------------------------------------------------------------------------
# O cache evita que a planilha seja lida novamente a cada interação do usuário.
@st.cache_data(ttl=600) # ttl=600 significa que o cache dura 10 minutos
def get_google_sheet_data(sheet_title: str, worksheet_name: str) -> pd.DataFrame:
    """
    Autentica no Google Sheets usando st.secrets e carrega o DataFrame.
    """
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


# -------------------------------------------------------------------------
# FUNÇÃO PRINCIPAL DE ETL (T e L)
# -------------------------------------------------------------------------

def format_cols(df: pd.DataFrame, columns_int: list = None, columns_float: list = None, columns_date: list = None):
    if not columns_int:
        columns_int = [
            "kids_presentes",
            "kids",
            "convidados_presentes",
            "convidados_previstos",
            "total_convidados_previsto",
            "total_convidados_presentes",
        ]
    
    if not columns_float:
        columns_float = [
            "sinal",
            "preço_kids",
            "valor_extra",
            "preço",
            "valor_total_previsto",
            "valor_total_realizado",
        ]

    if not columns_date:
        columns_date = ["data_contato", "data_evento"]

    df[columns_int] = df[columns_int].apply(lambda x: x.astype(int))
    df[columns_float] = df[columns_float].apply(lambda x: x.astype(float))
    df[columns_date] = df[columns_date].apply(
        lambda x: pd.to_datetime(x, errors="coerce", dayfirst=True)
    )
    return df

# Função para cálculos dependentes da etapa do evento
def calculos_automaticos(df: pd.DataFrame) -> pd.DataFrame:
    df["manter_total_previsto"] = df["manter_total_previsto"].astype(bool)
    df["total_convidados_previsto"] = df["convidados_previstos"] + df["kids"]
    df["valor_total_previsto"] = (df.preço * df.convidados_previstos) + (
        df.kids * df.preço_kids
    )
    # Total de presentes é 0 se etapa != 'Realizado'
    df["total_convidados_presentes"] = np.where(
        df["etapa"] == "Realizado",
        df["convidados_presentes"] + df["kids_presentes"],
        0,
    )
    
    # Lógica para cálculo do valor realizado
    cond1 = (df["etapa"] == "Realizado") & (df["manter_total_previsto"] == True)
    cond2 = (df["etapa"] == "Realizado") & (df["manter_total_previsto"] == False)

    choice1 = df["valor_total_previsto"] + df["valor_extra"]
    # Recalcula baseado nos presentes se manter_total_previsto for False
    choice2 = (
        (df["convidados_presentes"] * df["preço"])
        + (df["kids_presentes"] * df["preço_kids"])
        + df["valor_extra"]
    )

    default = 0

    # Aplica as condições para calcular valor_total_realizado
    df["valor_total_realizado"] = np.select(
        [cond1, cond2], [choice1, choice2], default=default
    )

    return df

def run_full_etl(sheet_title: str = "Prog_eventos_thai_house", worksheet_name: str = "Completa") -> pd.DataFrame:
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
    # A variável df_thai recebe os dados do Google Sheets
    df_thai = get_google_sheet_data(sheet_title, worksheet_name)

    # VERIFICAÇÃO BÁSICA
    if df_thai.empty:
        print("Erro ao carregar dados ou DataFrame vazio.")
        return df_thai
    else:
        # --- Organização e Conversão de Tipos (DataFrame Atual) ---
        # Renomeia colunas para minúsculas e substitui espaços por underscores
        colunas_lower_replace(df)

        columns_manter = [
            "local", "kids_presentes", "sinal", "resp", "empresa", "cardápio", "kids",
            "preço_kids", "convidados_presentes", "convidados_previstos", "forma_de_pagamento",
            "etapa", "telefone", "valor_extra", "horário_início", "situação", "email",
            "data_contato", "observação", "data_evento", "preço", "tipo", "contato",
            "manter_total_previsto",
        ]

        columns_int = ["kids_presentes", "kids", "convidados_presentes", "convidados_previstos"]
        columns_float = ["sinal", "preço_kids", "valor_extra", "preço"]
        numeric_cols = columns_float + columns_int

        df = df[columns_manter].copy()

        # Converte 'manter_total_previsto' para booleano
        df["manter_total_previsto"] = np.where(
            df["manter_total_previsto"] == "FALSE", 0, 1
        ).astype(bool)

        df = df.replace("", np.nan)

        # Converte colunas numéricas de string (com vírgula) para float
        df[numeric_cols] = (
            df[numeric_cols].apply(lambda x: x.str.replace(",", ".")).astype(float)
        )


        # Leitura do dados dos anos anteriores
        try:
            df_anos_ant = get_google_sheet_data(sheet_title='dados_anos_anteriores', worksheet_name='Sheet1')

        except FileNotFoundError:
            print(f"Erro: Arquivo de dados de anos anteriores não encontrado. Continuando com DataFrame atual apenas.")
            df_anos_ant = pd.DataFrame(columns=columns_manter)

        if not df_anos_ant.empty:
            # Formata datas para o padrão do DataFrame atual
            df_anos_ant["data_contato"] = pd.to_datetime(
                df_anos_ant["data_contato"]
            ).dt.strftime("%d/%m/%Y")
            df_anos_ant["data_evento"] = pd.to_datetime(
                df_anos_ant["data_evento"]
            ).dt.strftime("%d/%m/%Y")

            df_anos_ant.insert(1, "local", "Thai House")

            # Padroniza nomes de colunas
            df_anos_ant.rename(
                columns={"resp_evento": "resp", "qtde_convidados": "convidados_previstos"},
                inplace=True,
            )

            # Mantém apenas as colunas necessárias para concatenação
            df_anos_ant = df_anos_ant.drop(
                columns=list(set(df_anos_ant.columns.tolist()) - set(columns_manter))
            )

            df_anos_ant["manter_total_previsto"] = True

        # Concatena os DataFrames
        df_thai = pd.concat([df_anos_ant, df], axis=0, join="outer", ignore_index=True)

        df_thai.reset_index(drop=True, inplace=True)

        # --- Tratamento de Missing Values e Tipos (DataFrame Combinado) ---

        # Preenche strings ausentes com "Não Informado"
        string_cols = [
            "local", "situação", "tipo", "empresa", "contato", "telefone", 
            "email", "cardápio", "forma_de_pagamento", "observação",
        ]
        df_thai[string_cols] = df_thai[string_cols].fillna("Não Informado")

        df_thai["horário_início"] = df_thai["horário_início"].fillna("00:00")

        # Preenche numéricos ausentes com 0.0 e 0, respectivamente
        df_thai[columns_float] = df_thai[columns_float].fillna(0.0).astype(float)
        df_thai[columns_int] = df_thai[columns_int].fillna(0).astype(int)

        # Tratamento e conversão de colunas de Data/Hora
        df_thai["horário_início"] = df_thai["horário_início"].str.replace(
            ";", ":", regex=False
        )
        df_thai["data_contato"] = pd.to_datetime(
            df_thai["data_contato"], errors="coerce", dayfirst=True
        )
        df_thai["data_evento"] = pd.to_datetime(
            df_thai["data_evento"], errors="coerce", dayfirst=True
        )
        df_thai["horário_início"] = pd.to_datetime(
            df_thai["horário_início"], format="%H:%M", errors="coerce"
        ).dt.time

        # Preenche 'data_contato' com 'data_evento' onde for nulo
        df_thai["data_contato"] = df_thai.data_contato.fillna(df_thai.data_evento)

        # Preenche 'data_evento' futuro para nulos
        dia = dt.today().date() + pd.DateOffset(days=20)
        df_thai["data_evento"] = pd.to_datetime(df_thai.data_evento.fillna(dia))

        # Aplica os cálculos automáticos na base consolidada
        df_thai = calculos_automaticos(df_thai)

        # --- Organização e Padronização de Strings ---

        # Remove caracteres especiais do 'contato' (mantendo apenas letras e números)
        char_esp = re.compile(r"\W+", re.MULTILINE)
        df_thai["contato"] = df_thai.contato.replace(char_esp, " ", regex=True)

        # Limpa, padroniza caixa baixa e capitaliza (título) todas as colunas string
        df_thai = df_thai.apply(
            lambda x: x.astype(str).str.strip().str.casefold().str.capitalize()
        )

        # Remove múltiplos espaços em branco
        regex_blank = re.compile(r"\s+", flags=re.MULTILINE)
        df_thai = df_thai.apply(lambda x: x.str.replace(regex_blank, " ", regex=True))

        # Remove a palavra "Menu" do cardápio e aplica título
        regex_menu = re.compile(r"[Menu]{4}(\s)?", flags=re.MULTILINE)
        df_thai["cardápio"] = df_thai.cardápio.str.replace(
            regex_menu, "", regex=True
        ).str.title()

        df_thai["empresa"] = df_thai["empresa"].str.title()
        df_thai["contato"] = df_thai["contato"].str.title()

        # Padroniza nomes de cardápios com erros de digitação comuns
        df_thai["cardápio"] = (
            df_thai.cardápio.replace("Ko Lanta", "Koh Lanta")
            .replace("Ko Pee Pee", "Koh Pee Pee")
            .replace("Ko Sak", "Koh Sak")
            .replace("Dia Dos Namorados", "Namorados")
            .replace("Koh Sammet", "Koh Samet")
        )

        # Define listas de cardápios válidos
        fast = ["kafae", "ma-li", "pi-leh", "ko mattra", "koh kood",]
        padrao = ["Phuket", "Koh Pee Pee", "Koh Sak", "Koh Lanta", "Ko mai Thon", "ko nom sao"]
        economico = ["koh samet", "krab", "krab"]
        nao_definido = ["Não Informado", "a definir"]
        card_river = ["Sushi-01", "Sushi-02", "Sushi-03"]

        menu_completo = list(set(item.lower() for item in (fast + padrao + economico + nao_definido + card_river)))

        # Substitui cardápios que não estão na lista de padronização por "Especial"
        condition = ~df_thai["cardápio"].str.lower().isin(menu_completo)
        df_thai.loc[condition, "cardápio"] = "Especial"

        # Ordena o DataFrame pela data do evento
        df_thai = df_thai.sort_values("data_evento", ignore_index=True)

        # Salva o DataFrame finalizado
        # df_thai.to_excel(r"dados/df_thai_finalizado.xlsx", index=False)

        
        
        print('Leitura e processamento realizados.')

        return format_cols(df_thai)

if __name__ == "__main__":
    print(run_full_etl())
#     final_df = run_full_etl()
#     if final_df is not None:
#         print(final_df.head())