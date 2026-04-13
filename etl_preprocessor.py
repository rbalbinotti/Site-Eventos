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
    from arq_py.mod_func import ( # pyright: ignore[reportMissingImports]
        colunas_lower_replace,
        whitespace_remover,
    )  # Funções auxiliares (biblioteca local)
except:
    from mod_func import colunas_lower_replace, whitespace_remover

warnings.filterwarnings("ignore")

# -------------------------------------------------------------------------
# FUNÇÃO DE EXTRAÇÃO DE DADOS (E do ETL) - USO EXCLUSIVO DO STREAMLIT CLOUD
# -------------------------------------------------------------------------
# O cache evita que a planilha seja lida novamente a cada interação do usuário.
# @st.cache_data(ttl=600) # ttl=600 significa que o cache dura 10 minutos
def get_google_sheet_data(
    sheet_title: str, worksheet_name: str, local: bool = False
) -> pd.DataFrame:

    if local:

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

        print(f"Dados carregados de: {sheet_title} - {worksheet_name}")
        return df

    else:

        """
        Autentica no Google Sheets e carrega o DataFrame.
        """
        service_account = "/home/rb/Dropbox/thai_house/thai/cred/credential_thai.json"

        # 2. Autentica o gspread LENDO DIRETAMENTE DO ARQUIVO
        try:
            gc = gspread.service_account(filename=service_account)
        except FileNotFoundError:
            # Use um print simples ou raise/logging, já que st.error só funciona no ambiente Streamlit
            print(
                f"Erro: O arquivo de credenciais não foi encontrado em {service_account}"
            )
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

        print(f"Dados carregados de: {sheet_title} - {worksheet_name}")
        return df

        # try:
        #     gcp_service_account_dict = dict(st.secrets["gcp_service_account"])
        # except KeyError:
        #     st.error("❌ Seção 'gcp_service_account' não encontrada nos Secrets.")
        #     st.info("Configure os Secrets no Streamlit Cloud conforme documentação.")
        #     return pd.DataFrame()
        # except Exception as e:
        #     st.error(f"Erro ao ler secrets: {e}")
        #     return pd.DataFrame()
        
        # try:
        #     gc = gspread.service_account_from_dict(gcp_service_account_dict)
        #     sh = gc.open(sheet_title)
        #     worksheet = sh.worksheet(worksheet_name)
        #     data = worksheet.get_all_values()
        #     df = pd.DataFrame(data[1:], columns=data[0])
        #     print(f"Dados carregados de: {sheet_title} - {worksheet_name}")
        #     return df
        # except Exception as e:
        #     st.error(f"❌ Falha ao conectar ao Google Sheets: {e}")
        #     return pd.DataFrame()


# -------------------------------------------------------------------------
# FUNÇÃO PRINCIPAL DE ETL (T e L)
# -------------------------------------------------------------------------


def format_cols(
    df: pd.DataFrame,
    columns_int: list = None,
    columns_float: list = None,
    columns_date: list = None,
):
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

    df[columns_int] = df[columns_int].astype(float).astype("uint16")
    df[columns_float] = df[columns_float].astype("float32").round()
    df[columns_date] = df[columns_date].apply(
        lambda x: pd.to_datetime(x, errors="coerce", dayfirst=True)
    )
    df.columns = df.columns.astype(str).str.lower().str.strip().str.replace(" ", "_")
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


def run_full_etl(
    sheet_title: str = "Prog_eventos_thai_house",
    worksheet_name: str = "Completa",
    local: bool = False,
) -> pd.DataFrame:
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
        y = get_google_sheet_data(sheet_title="dados_anos_anteriores", worksheet_name="Sheet1", local=True)
    except:
        X = get_google_sheet_data(sheet_title, worksheet_name, local=False)
        y = get_google_sheet_data(sheet_title="dados_anos_anteriores", worksheet_name="Sheet1", local=False)
    finally:
        print("\033[91m" + "Processo de carregamento concluído." + "\033[0m")
        # print("\033[91m" + "Tabela Atual" + "\033[0m" + f"\n{X.head(3)}")
        # print()
        # print()
        # print("\033[91m" + "Tabela Anos Anteriores" + "\033[0m" + f"\n{X.head(3)}")


    # --- Organização e Conversão de Tipos (DataFrame Atual) ---
    # Renomeia colunas para minúsculas e substitui espaços por underscores
    colunas_lower_replace(X)

    x_columns = X.columns.tolist()

    y_columns = y.columns.tolist()

    columns_manter = list(set(x_columns) - (set(x_columns) - set(y_columns)))

    # print(columns_manter)

    columns_int = ["kids_presentes", "kids", "convidados_presentes"]
    columns_float = ["sinal", "preço_kids", "valor_extra"]
    numeric_cols = columns_float + columns_int + ["convidados_previstos", "preço"]

    X = X[columns_manter].copy()

    # Converte 'manter_total_previsto' para booleano
    X["manter_total_previsto"] = np.where(
        X["manter_total_previsto"] == "FALSE", 0, 1
    ).astype(bool)

    X = X.replace("", np.nan)

    # Converte colunas numéricas de string (com vírgula) para float
    X[numeric_cols] = (
        X[numeric_cols].apply(lambda x: x.str.replace(",", ".")).astype(float)
    )

    # Preenche strings ausentes com "Não Informado"
    string_cols = [
        "local",
        "situação",
        "tipo",
        "empresa",
        "contato",
        "telefone",
        "email",
        "cardápio",
        "forma_de_pagamento",
        "observação",
    ]
    X[string_cols] = X[string_cols].fillna("Não Informado")
    X[string_cols] = X[string_cols].apply(lambda x: x.str.lower())

    X["horário_início"] = X["horário_início"].fillna("00:00")

    # Tratamento preços ausentes
    media_preco_thai = (
        X.query('local == "thai house"')["preço"].mean().astype(float).round()
    )
    media_preco_river = (
        X.query('local == "river"')["preço"].mean().astype(float).round()
    )
    X["preço"] = np.where(
        (X["local"] == "thai house") & (X["preço"].isna()),
        media_preco_thai,
        np.where(
            (X["local"] == "river") & (X["preço"].isna()),
            media_preco_river,
            X["preço"],
        ),
    )

    # Tratamento convidados ausentes
    media_convidados_thai = (
        X.query('local == "thai house"')["convidados_previstos"].mean().round()
    )
    media_convidados_river = (
        X.query('local == "river"')["convidados_previstos"].mean().round()
    )
    X["convidados_previstos"] = np.where(
        (X["local"] == "thai house") & (X["convidados_previstos"].isna()),
        media_convidados_thai,
        np.where(
            (X["local"] == "river") & (X["convidados_previstos"].isna()),
            media_convidados_river,
            X["convidados_previstos"],
        ),
    )

    # Demais dados ausentes preenchidos com zero
    X[columns_int] = X[columns_int].fillna(int(0))
    X[columns_float] = X[columns_float].fillna(0)



    # Formata datas para o padrão do DataFrame atual
    y["data_contato"] = pd.to_datetime(
        y["data_contato"]
    ).dt.strftime("%d/%m/%Y")
    y["data_evento"] = pd.to_datetime(
        y["data_evento"]
    ).dt.strftime("%d/%m/%Y")

    # Padroniza nomes de colunas
    y.rename(
        columns={
            "resp_evento": "resp",
            "qtde_convidados": "convidados_previstos",
        },
        inplace=True,
    )

    # Concatena os DataFrames
    df_completo = pd.concat(
        [y, X], axis=0, join="outer", ignore_index=True
    )

    df_completo.reset_index(drop=True, inplace=True)

    # Converte colunas numéricas
    df_completo[numeric_cols] = df_completo[numeric_cols].astype(float)

    # --- Tratamento de Missing Values e Tipos (DataFrame Combinado) ---

    # Tratamento e conversão de colunas de Data/Hora
    df_completo["horário_início"] = df_completo["horário_início"].str.replace(
        ";", ":", regex=False
    )
    df_completo["data_contato"] = pd.to_datetime(
        df_completo["data_contato"], errors="coerce", dayfirst=True
    )
    df_completo["data_evento"] = pd.to_datetime(
        df_completo["data_evento"], errors="coerce", dayfirst=True
    )
    # df_completo["horário_início"] = pd.to_datetime(
    #     df_completo["horário_início"], format="%H:%M", errors="coerce"
    # ).dt.time

    # Preenche 'data_contato' com 'data_evento' onde for nulo
    df_completo["data_contato"] = df_completo.data_contato.fillna(
        df_completo.data_evento
    )

    # Preenche 'data_evento' futuro para nulos
    dia = dt.today().date() + pd.DateOffset(days=20)
    df_completo["data_evento"] = pd.to_datetime(df_completo.data_evento.fillna(dia))

    # Aplica os cálculos automáticos na base consolidada
    df_completo = calculos_automaticos(df_completo)

    # --- Organização e Padronização de Strings ---

    # Remove caracteres especiais do 'contato' (mantendo apenas letras e números)
    char_esp = re.compile(r"\W+", re.MULTILINE)
    df_completo["contato"] = df_completo.contato.replace(char_esp, " ", regex=True)

    # Limpa, padroniza caixa baixa e capitaliza (título) todas as colunas string
    df_completo = df_completo.apply(
        lambda col: (
            col.astype(str).str.strip().str.casefold().str.capitalize()
            if col.name != "email"
            else col
        )
    )

    # Remove múltiplos espaços em branco
    regex_blank = re.compile(r"\s+", flags=re.MULTILINE)
    df_completo = df_completo.apply(
        lambda x: x.str.replace(regex_blank, " ", regex=True)
    )

    # Remove a palavra "Menu" do cardápio e aplica título
    regex_menu = re.compile(r"[Menu]{4}(\s)?", flags=re.MULTILINE)
    df_completo["cardápio"] = df_completo.cardápio.str.replace(
        regex_menu, "", regex=True
    ).str.title()

    df_completo["empresa"] = df_completo["empresa"].str.title()
    df_completo["contato"] = df_completo["contato"].str.title()

    # Padroniza nomes de cardápios com erros de digitação comuns
    df_completo["cardápio"] = (
        df_completo.cardápio.replace("Ko Lanta", "Koh Lanta")
        .replace("Ko Pee Pee", "Koh Pee Pee")
        .replace("Ko Sak", "Koh Sak")
        .replace("Dia Dos Namorados", "Namorados")
        .replace("Koh Sammet", "Koh Samet")
    )

    # Define listas de cardápios válidos
    fast = [
        "kafae",
        "ma-li",
        "pi-leh",
        "ko mattra",
        "koh kood",
    ]
    padrao = [
        "Phuket",
        "Koh Pee Pee",
        "Koh Sak",
        "Koh Lanta",
        "Ko mai Thon",
        "ko nom sao",
    ]
    economico = ["koh samet", "krab", "krab"]
    nao_definido = ["Não Informado", "a definir"]
    card_river = ["Sushi-01", "Sushi-02", "Sushi-03"]

    menu_completo = list(
        set(
            item.lower()
            for item in (fast + padrao + economico + nao_definido + card_river)
        )
    )

    # Substitui cardápios que não estão na lista de padronização por "Especial"
    condition = ~df_completo["cardápio"].str.lower().isin(menu_completo)
    df_completo.loc[condition, "cardápio"] = "Especial"

    # Ordena o DataFrame pela data do evento
    df_completo = df_completo.sort_values("data_evento", ignore_index=True)

    # Remove colunas desnecessárias
    drop_columns = ['tipo', 'email', 'situação', 'resp', 'contato', 'observação', 'telefone', 'forma_de_pagamento', 'ano_evento', 'mes_evento', 'dia_semana', 'cod_etapa', 'manter_total_previsto', 'data_contato']
    df_completo = df_completo.drop(
        columns=drop_columns
     )

    # df_completo.columns = df_completo.columns.str.title().str.replace("_", " ")
    df_completo["data_evento"] = pd.to_datetime(
        df_completo["data_evento"], errors="coerce", dayfirst=True
    )
    int_cols = ['convidados_previstos', 'kids', 'convidados_presentes', 'kids_presentes', 'total_convidados_previsto', 'total_convidados_presentes']
    float_cols = ['preço', 'preço_kids', 'sinal', 'valor_extra', 'valor_total_previsto', 'valor_total_realizado']

    # df_completo[int_cols] = df_completo[int_cols].astype(np.int32)
    df_completo[float_cols + int_cols] = df_completo[float_cols + int_cols].astype(np.float32)

    print("Leitura e processamento realizados.")

    return df_completo


if __name__ == "__main__":
    df = run_full_etl(
        sheet_title="Prog_eventos_thai_house", worksheet_name="Completa", local=True
    )
    print(df.info())
