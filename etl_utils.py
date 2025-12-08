"""
MÓDULO DE UTILIDADES PARA ETL (EXTRAÇÃO, TRANSFORMAÇÃO E CARGA)

Este módulo contém classes e funções para pré-processamento, filtragem
e geração de relatórios consolidados (DRE) a partir de dados de eventos
armazenados em DataFrames do pandas.

Classes:
- DataProcess: Realiza transformações como criação de categorias e extração de datas.
- FilterSelection: Aplica filtros no DataFrame com base em local, etapa e ano.

Funções:
- dre: Gera quatro DataFrames de relatórios consolidados (financeiro e participação).
"""

# bibliotecas
import locale
import pandas as pd
import numpy as np
from datetime import date
from dateutil.relativedelta import relativedelta

# Configura o locale para português do Brasil, essencial para o dt.strftime funcionar
# corretamente com nomes de meses e dias da semana em português.
# locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

# Try different locale options
locales_to_try = ["pt_BR.UTF-8", "pt_BR", "Portuguese_Brazil.1252", "C.UTF-8", "C"]

for loc in locales_to_try:
    try:
        locale.setlocale(locale.LC_ALL, loc)
        print(f"Locale set to: {loc}")
        break
    except locale.Error:
        continue
else:
    # If none work, use default
    locale.setlocale(locale.LC_ALL, "")


class DataProcess:
    """
    Classe para processamento de dados de eventos (Transformação - T do ETL).

    Permite:
    1. Criar colunas categóricas e seus códigos numéricos a partir de uma coluna existente.
    2. Extrair informações de data (ano, mês e dia da semana) de uma coluna de datas.
    3. Consolidar todas as transformações em um único método.

    Atributos
    ----------
    cat_col : str
        Nome da coluna categórica a ser processada (padrão: 'etapa').
    data_col : str
        Nome da coluna de datas a ser processada (padrão: 'data_evento').
    """

    def __init__(self, cat_col: str = 'etapa', data_col: str = 'data_evento'):
        """
        Inicializa a classe DataProcess.

        Parameters
        ----------
        cat_col : str, optional
            Nome da coluna categórica (default é 'etapa').
        data_col : str, optional
            Nome da coluna de datas (default é 'data_evento').
        """
        self.cat_col = cat_col  # Coluna para criar categoria/código
        self.data_col = data_col  # Coluna para extrair informações de data

    def _create_category(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cria uma coluna categórica e gera códigos numéricos.

        Aplica as seguintes transformações:
        - Converte a coluna de datas para o tipo datetime (garante a tipagem correta).
        - Converte a coluna categórica (self.cat_col) para o tipo 'category'.
        - Cria a coluna "cod_{self.cat_col}" com os códigos numéricos.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame de entrada.

        Returns
        -------
        pd.DataFrame
            DataFrame com colunas de data tipada, categoria e códigos adicionadas.
        """
        df_copy = df.copy()
        # Garante que a coluna de data esteja no formato datetime, essencial para extração
        df_copy[self.data_col] = pd.to_datetime(df_copy[self.data_col])
        # Transforma a coluna em tipo 'category' para otimizar memória e permitir codificação
        df_copy[self.cat_col] = df_copy[self.cat_col].astype('category')
        # Gera códigos numéricos únicos para cada categoria
        df_copy["cod_" + self.cat_col] = df_copy[self.cat_col].cat.codes
        return df_copy

    def _process_date(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extrai o ano, o mês abreviado e o dia da semana da coluna de datas.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame que já deve ter a coluna de datas no formato datetime.

        Returns
        -------
        pd.DataFrame
            DataFrame com as colunas 'ano_evento', 'mes_evento' e 'dia_semana' adicionadas.
        """
        df_copy = df.copy()
        df_copy['ano_evento'] = df_copy[self.data_col].dt.year  # Extrai o ano
        # Extrai o mês abreviado (e.g., 'Jan', 'Fev'), usando o locale 'pt_BR'
        df_copy['mes_evento'] = df_copy[self.data_col].dt.strftime('%b')
        # Extrai o nome completo do dia da semana (e.g., 'Segunda-feira'), usando o locale 'pt_BR'
        df_copy["dia_semana"] = df_copy[self.data_col].dt.strftime("%A")
        return df_copy

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica todas as transformações de categoria e data no DataFrame de forma consolidada.

        Passos:
        1. Cria categorias e códigos (_create_category).
        2. Extrai informações de data (_process_date).
        3. Formata os nomes das colunas (substitui '_' por espaço e capitaliza).

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame original.

        Returns
        -------
        pd.DataFrame
            DataFrame processado com todas as colunas adicionais e nomes formatados.
        """
        # Aplica a criação de categorias e códigos
        df_processed = self._create_category(df)
        # Aplica a extração das informações de data
        df_processed = self._process_date(df_processed)
        # Formata os nomes das colunas para melhor visualização (e.g., 'data_evento' -> 'Data evento')
        df_processed.columns = df_processed.columns.str.replace('_', ' ').str.capitalize()

        return df_processed


class FilterSelection:
    """
    Classe para aplicar filtros no DataFrame de eventos com base em critérios
    pré-definidos de local, etapa e ano.

    Atributos
    ----------
    place_select : list[str] | None
        Lista de locais para filtro (e.g., ['São Paulo', 'Rio de Janeiro']).
    stage_select : list[str] | None
        Lista de etapas para filtro (e.g., ['Prospecção', 'Fechamento']).
    year_select : int | None
        Ano específico para filtro (e.g., 2024).
    """

    def __init__(self, place_select: list[str] = None, stage_select: list[str] = None, year_select: int = None):
        """
        Inicializa a classe FilterSelection com os critérios de filtro.
        """
        self.place_select = place_select
        self.stage_select = stage_select
        self.year_select = year_select

    def run_filter(
        self,
        df: pd.DataFrame,
        filter_place: bool = True,
        filter_stage: bool = True,
        filter_year: bool = True,
    ) -> pd.DataFrame:
        """
        Aplica os filtros configurados (local, etapa, ano) ao DataFrame de entrada.

        O método espera que o DataFrame tenha as colunas: 'Local', 'Etapa', 'Ano evento'.
        A filtragem usa o método isin() para listas e a comparação direta para o ano.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame de dados de eventos (já processado).
        filter_place : bool, optional
            Se True, aplica o filtro por Local (default = True).
        filter_stage : bool, optional
            Se True, aplica o filtro por Etapa (default = True).
        filter_year : bool, optional
            Se True, aplica o filtro por Ano evento (default = True).

        Returns
        -------
        pd.DataFrame
            DataFrame com as linhas filtradas.
        """

        # Cria uma cópia para evitar side effects no DataFrame original
        df_filtered = df.copy()

        # 1. Filtro por Local
        if filter_place and self.place_select:
            # Filtra onde a coluna 'Local' está na lista 'place_select'
            df_filtered = df_filtered[df_filtered['Local'].isin(self.place_select)]
        elif filter_place:
            # Mensagem de aviso se o filtro foi ativado, mas os critérios estão vazios
            print("Atenção: 'filter_place' é True, mas 'place_select' está vazio ou é None. Nenhum filtro de local aplicado.")

        # 2. Filtro por Etapa
        if filter_stage and self.stage_select:
            # Filtra onde a coluna 'Etapa' está na lista 'stage_select'
            df_filtered = df_filtered[df_filtered['Etapa'].isin(self.stage_select)]
        elif filter_stage:
            print("Atenção: 'filter_stage' é True, mas 'stage_select' está vazio ou é None. Nenhum filtro de etapa aplicado.")

        # 3. Filtro por Ano
        if filter_year and self.year_select is not None:
            # Filtra onde a coluna 'Ano evento' é igual ao 'year_select'
            df_filtered = df_filtered[df_filtered['Ano evento'] == self.year_select]
        elif filter_year:
            # O filtro por ano deve ser mais rígido, pois a falta de um ano pode indicar erro
            print("Atenção: 'filter_year' é True, mas 'year_select' é None. Nenhum filtro de ano aplicado.")

        return df_filtered


def dre(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Gera quatro relatórios consolidados (DRE - Demonstração do Resultado do Exercício)
    para análise de desempenho financeiro e de participação em eventos.

    Visões Geradas:
    1. df_melted_valor: Valores (Previsto/Realizado) por Local e Etapa do MÊS ANTERIOR.
    2. df_melted_convidados: Convidados (Previsto/Presentes) por Local e Etapa do MÊS ANTERIOR.
    3. df_grouped_local: Contagem de eventos por Etapa e Local do MÊS ANTERIOR.
    4. df_melt_prev_real: Valores (Previsto/Realizado) por Ano e Local, TODOS OS DADOS.

    O cálculo do mês anterior é baseado na data atual.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame de eventos processado, esperado ter as colunas:
        'Data evento', 'Ano evento', 'Local', 'Etapa', 'Valor total previsto',
        'Valor total realizado', 'Total convidados previsto', 'Total convidados presentes'.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]
        Uma tupla contendo os quatro DataFrames de relatório, na ordem listada acima.
    """
    # --- 1. Definição do Período de Análise (Mês Anterior) ---
    meses_retroativos = 1
    data_hoje = date.today()
    # Calcula o objeto date do mês anterior
    mes_anterior = data_hoje - relativedelta(months=meses_retroativos)

    # Filtra os dados apenas para o mês anterior (comparando o número do mês)
    df_mes_anterior = df[df["Data evento"].dt.month == mes_anterior.month].copy()

    # --- 2. Agrupamento para o Mês Anterior (Local/Etapa) ---
    # Agrupa por Local e Etapa, somando as métricas financeiras e de convidados
    df_grouped_mes_anterior = (
        df_mes_anterior.groupby(["Local", "Etapa"], dropna=False)[
            [
                "Valor total realizado",
                "Valor total previsto",
                "Total convidados previsto",
                "Total convidados presentes",
            ]
        ]
        .sum()
        .reset_index()
    )

    # --- 3. Geração dos Relatórios do Mês Anterior (formato longo - melt) ---

    # 3.1. Relatório Financeiro (Previsto vs Realizado)
    df_melted_valor = df_grouped_mes_anterior.melt(
        id_vars=["Local", "Etapa"],
        value_vars=["Valor total previsto", "Valor total realizado"],
        var_name="tipo",  # Nova coluna para indicar se é 'previsto' ou 'realizado'
        value_name="valor total",
    )
    # Renomeia os valores da coluna 'tipo' para um formato mais legível
    df_melted_valor["tipo"] = df_melted_valor["tipo"].replace(
        {"Valor total previsto": "Previsto", "Valor total realizado": "Realizado"}
    )

    # 3.2. Relatório de Participação (Previsto vs Presentes)
    df_melted_convidados = df_grouped_mes_anterior.melt(
        id_vars=["Local", "Etapa"],
        value_vars=["Total convidados previsto", "Total convidados presentes"],
        var_name="tipo",
        value_name="total convidados",
    )
    # Renomeia os valores da coluna 'tipo'
    df_melted_convidados["tipo"] = df_melted_convidados["tipo"].replace(
        {"Total convidados previsto": "Previsto", "Total convidados presentes": "Presentes"}
    )

    # 3.3. Relatório de Contagem de Eventos (por Etapa e Local)
    df_grouped_local = (
        df_mes_anterior.groupby(["Etapa", "Local"], dropna=False)
        .size()  # Conta o número de linhas em cada grupo
        .reset_index(name="Contagem Etapa")
    )

    # --- 4. Relatório Acumulado Geral (Todos os Dados) ---
    # Transforma os valores financeiros em formato longo, agrupando por Ano e Local
    df_melt_prev_real = df.melt(
        id_vars=["Ano evento", "Local"],
        value_vars=["Valor total previsto", "Valor total realizado"],
        var_name="tipo",
        value_name="valor total acumulado",
    )
    # Renomeia os valores da coluna 'tipo'
    df_melt_prev_real["tipo"] = df_melt_prev_real["tipo"].replace(
        {"Valor total previsto": "Previsto", "Valor total realizado": "Realizado"}
    )

    # Retorna os quatro DataFrames gerados
    return df_melted_valor, df_melted_convidados, df_grouped_local, df_melt_prev_real