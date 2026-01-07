import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta
from typing import Dict, Any, Tuple, Union, List


# =========================================================================
# FUNÇÕES AUXILIARES PARA CRIAÇÃO DE GRÁFICOS
# =========================================================================

def config_plot(
    plot: Union[px.bar, px.histogram, px.pie],
    legend: str = None,
    ord_date: bool = False,
    invert_x_axis: bool = False,
    showtick: bool = True
) -> Union[px.bar, px.histogram, px.pie]:
    """
    Configurações padronizadas de layout e estilo para gráficos Plotly.

    Aplica ajustes como ordenação do eixo X (para meses), formatação de texto nas barras
    e configurações de exibição do eixo Y.

    :param plot: Objeto Plotly Figure (px.bar, px.histogram, etc.).
    :type plot: Union[px.bar, px.histogram, px.pie]
    :param legend: Nome da coluna usada para a cor, se houver. Se None, a legenda não é exibida.
    :type legend: str, optional
    :param ord_date: Se True, tenta ordenar o eixo X cronologicamente para meses.
    :type ord_date: bool, optional
    :param invert_x_axis: Se True, ajusta o eixo Y com dtick=1 (útil para gráficos horizontais).
    :type invert_x_axis: bool, optional
    :param showtick: Se False, oculta os rótulos do eixo Y.
    :type showtick: bool, optional
    :returns: O objeto Plotly Figure configurado.
    :rtype: Union[px.bar, px.histogram, px.pie]
    """
    # Exibe legenda apenas se houver coluna definida para cores
    show = True if legend else False

    # Ordenação cronológica dos meses, se solicitado
    asc_date = (
        ("jan", "fev", "mar", "abr", "mai", "jun",
         "jul", "ago", "set", "out", "nov", "dez")
        if ord_date else None
    )

    # Ajustes de layout e estilo do gráfico
    # Configura o eixo Y, usando dtick=1 se for um gráfico "invertido" (horizontal)
    if invert_x_axis:
        plot.update_yaxes(title=None, showticklabels=showtick, dtick=1)
    else:
        plot.update_yaxes(title=None, showticklabels=showtick)

    # Configura o eixo X, aplicando ordenação de meses se `ord_date` for True
    plot.update_xaxes(title=None, categoryarray=asc_date)

    # Adiciona o valor 'y' formatado como texto sobre as barras
    plot.update_traces(texttemplate="%{y:,.0f}", textposition="outside")

    # Configurações gerais de layout
    plot.update_layout(title="", bargap=0.1, separators=",.", showlegend=show)

    return plot


def plot_hist(df: pd.DataFrame, x_axis: str = None, y_axis: str = None, color: str = 'Local') -> px.histogram:
    """
    Cria um histograma Plotly Express simples com configurações básicas.

    :param df: DataFrame de entrada.
    :type df: pd.DataFrame
    :param x_axis: Coluna para o eixo X.
    :type x_axis: str, optional
    :param y_axis: Coluna para o eixo Y.
    :type y_axis: str, optional
    :param color: Coluna para colorir as barras (agrupamento).
    :type color: str, optional
    :returns: O objeto Figure do Plotly (px.histogram).
    :rtype: px.histogram
    """
    hist = px.histogram(
        df,
        x=x_axis,
        y=y_axis,
        text_auto=True,
        color=color,
        # Define a ordem das categorias de cor (Local)
        category_orders={"Local": ["Thai house", "River"]}
    )
    return hist


def plot_hztl(df: pd.DataFrame, select_month: bool = False) -> px.histogram:
    """
    Cria um gráfico de barras horizontais comparando Convidados Previstos vs. Presentes.

    O gráfico é facetado pelo 'Local' e agrupa por 'Ano evento' ou 'Mes evento'.

    :param df: DataFrame de eventos brutos.
    :type df: pd.DataFrame
    :param select_month: Se True, agrupa por mês ('Mes evento'); caso contrário, por ano ('Ano evento').
    :type select_month: bool, optional
    :returns: O objeto Figure do Plotly (px.histogram).
    :rtype: px.histogram
    """
    # Define a variável de agrupamento (Mês ou Ano)
    var_date = 'Mes evento' if select_month else 'Ano evento'

    # Filtra apenas eventos do ano de 2024 em diante
    df_plus2024 = df[df['Ano evento'] > 2024]

    # Transforma os dados de colunas ('Previsto', 'Presentes') para linhas (formato 'long')
    df_long = df_plus2024.rename(columns={
        'Total convidados previsto': 'Previsto',
        'Total convidados presentes': 'Presentes'
    }).melt(
        id_vars=[var_date, 'Local'],
        value_vars=['Previsto', 'Presentes'],
        var_name='Tipo',
        value_name='Convidados'
    )

    # Cria o histograma horizontal, facetado por 'Local' e colorido por 'Tipo' (Previsto/Presentes)
    plot_conv = px.histogram(
        df_long,
        orientation='h',
        x=['Convidados'],
        y=var_date,
        color='Tipo',
        facet_row='Local',
        text_auto=True
    )

    # Ajustes de layout específicos para este gráfico
    plot_conv.update_xaxes(title=None, showticklabels=False) # Remove rótulos do eixo X (horizontal)
    plot_conv.update_yaxes(dtick=1, title=None) # Garante um tick para cada mês/ano
    plot_conv.update_layout(bargap=0.1, showlegend=True)

    return plot_conv


def plot_pie(df: pd.DataFrame, col_plot: str) -> px.pie:
    """
    Cria um gráfico de pizza (donut chart) facetado por 'Local' para uma coluna.

    :param df: DataFrame de entrada.
    :type df: pd.DataFrame
    :param col_plot: Coluna a ser usada para as fatias ('names').
    :type col_plot: str
    :returns: O objeto Figure do Plotly (px.pie).
    :rtype: px.pie
    """

    figpie = px.pie(
        df,
        names=col_plot,
        hole=0.7,  # Cria o formato de donut
        facet_col="Local" # Cria um gráfico de pizza para cada Local
    )

    # Configura o texto para exibir percentual e rótulo dentro da fatia
    figpie.update_traces(textposition="inside", textinfo="percent+label")

    # Configurações gerais de layout
    figpie.update_layout(showlegend=False, title='')

    return figpie


def create_table(df: pd.DataFrame, etapa_select: str, previsto: bool) -> pd.DataFrame:
    """
    Filtra e formata um DataFrame de eventos para exibição em tabela.

    Filtra pela 'Etapa' e adiciona uma linha de 'Total' para as colunas numéricas.
    Formata a data para exibição simplificada.

    :param df: DataFrame de eventos brutos.
    :type df: pd.DataFrame
    :param etapa_select: O valor da 'Etapa' do evento a ser filtrado (ex: 'Negociação').
    :type etapa_select: str
    :param previsto: Se True, inclui 'Valor total previsto'; caso contrário, 'Valor total realizado'.
    :type previsto: bool
    :returns: O DataFrame filtrado, formatado e com linha de total.
    :rtype: pd.DataFrame
    """

    # Colunas base e colunas de valor (previsto ou realizado)
    cols = ["Resp", "Local","Etapa","Total convidados previsto","Data evento","Horário início","Empresa","Contato"]
    filter_cols = cols + ["Valor total previsto"] if previsto else cols + ['Valor total realizado']

    # Filtra o DataFrame pela Etapa selecionada e seleciona as colunas
    process = df.loc[:, filter_cols].query('Etapa == @etapa_select').copy() # Adicionado .copy() para evitar SettingWithCopyWarning

    # CORREÇÃO PARA CATEGORICAL DTYPE:
    # Converte a coluna 'Etapa' para tipo 'object' (string) antes de tentar
    # atribuir um valor que não é uma categoria existente (como "" ou NaN) à linha 'Total'.
    if 'Etapa' in process.columns:
        process['Etapa'] = process['Etapa'].astype('object')

    # Formata a coluna de data
    process["Data evento"] = process['Data evento'].dt.strftime("%x")

    # Calcula e adiciona a linha de 'Total' (soma apenas colunas numéricas)
    total_row = process.sum(numeric_only=True)
    process.loc["Total"] = total_row

    # Ajustes finais de formatação na linha de total e NaN
    process.loc["Total", "Etapa"] = "" # Limpa a Etapa na linha de Total (agora é seguro, pois é 'object')
    process["Etapa"] = process['Etapa'].astype(str).replace("nan", "")
    process.fillna("", inplace=True)

    return process


# =========================================================================
# CLASSE: PAINEL DE EVENTOS CONSOLIDADO
# =========================================================================

class PainelEventos:
    """
    Classe para gerar um painel consolidado de gráficos de eventos (2x3 subplots).

    Encapsula a lógica de processamento de dados e a criação de gráficos
    comparativos de Faturamento e Convidados (Previsto vs. Realizado) por Local,
    além de uma contagem de eventos. A análise é focada em um mês retroativo.
    """

    # =========================================================================
    # CONSTANTES
    # =========================================================================
    MAPA_CORES_LOCAL = {
        "Thai house": "darkslategrey",
        "River": "darkolivegreen",
    }

    # Usado para renomear os nomes dos traces Plotly (eixo Y)
    MAPA_RENOMEACAO_DADOS = {
        "Valor total previsto": "Previsto",
        "Valor total realizado": "Realizado",
    }

    def __init__(self, n_meses_retroativos: int = 1):
        """
        Inicializa a classe PainelEventos.

        :param n_meses_retroativos: Número de meses para retroagir a partir da data atual
                                     para definir o período de análise.
        :type n_meses_retroativos: int, optional
        """
        self.n_meses_retroativos = n_meses_retroativos
        # Calcula o nome do mês para o título
        self.mes = self._calcular_mes_retroativo(n_meses_retroativos)
        self.titulo_geral = f"Relatório Consolidado de Eventos (Valor e Convidados Previsto/Realizado) - Mês de {self.mes}"


    # =========================================================================
    # MÉTODOS AUXILIARES (Privados)
    # =========================================================================

    def _calcular_mes_retroativo(self, n: int) -> str:
        """
        Define e retorna o nome do mês retroagido em 'n' meses a partir de hoje.

        :param n: Número de meses para retroagir.
        :type n: int
        :returns: Nome do mês retroagido (ex: "Novembro").
        :rtype: str
        """
        data_retroativa = date.today() - relativedelta(months=n)
        return data_retroativa.strftime("%B").capitalize()


    def _gerar_dataframes_analiticos(self, df_eventos_bruto: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Processa o DataFrame de eventos brutos para gerar os 4 DataFrames de análise
        (Faturamento Mês, Convidados Mês, Contagem Mês, Faturamento Acumulado).

        :param df_eventos_bruto: DataFrame contendo os dados brutos dos eventos.
        :type df_eventos_bruto: pd.DataFrame
        :returns: Uma tupla contendo os 4 DataFrames gerados:
                  (df_mes_fat_melt, df_mes_conv_melt, df_mes_contagem, df_acumulado_fat_melt).
        :rtype: Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]
        """

        # 1. Definição do período de análise e filtro
        data_hoje = date.today()
        # Data exata do mês retroativo
        data_retroativa = data_hoje - relativedelta(months=self.n_meses_retroativos)

        # Filtra apenas os eventos do mês e ano de análise
        df_eventos_mes_analise = df_eventos_bruto[
            (df_eventos_bruto["Data evento"].dt.month == data_retroativa.month) &
            (df_eventos_bruto["Data evento"].dt.year == data_retroativa.year)
        ].copy()

        # 2. Agrupamento para o Mês de Análise
        # Agrupa por Local e Etapa, somando os valores (financeiros e convidados)
        df_agrupado_mes_analise = (
            df_eventos_mes_analise.groupby(["Local", "Etapa"])[
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

        # 2a. Melt de Valores Financeiros (df_mes_fat_melt)
        df_mes_fat_melt = df_agrupado_mes_analise.melt(
            id_vars=["Local", "Etapa"],
            value_vars=["Valor total previsto", "Valor total realizado"],
            var_name="Tipo",
            value_name="Valor total",
        )
        # Renomeia os valores da coluna 'Tipo' para 'Previsto'/'Realizado'
        df_mes_fat_melt["Tipo"] = df_mes_fat_melt["Tipo"].replace(
            {"Valor total previsto": "Previsto", "Valor total realizado": "Realizado"}
        )

        # 2b. Melt de Convidados (df_mes_conv_melt)
        df_mes_conv_melt = df_agrupado_mes_analise.melt(
            id_vars=["Local", "Etapa"],
            value_vars=["Total convidados previsto", "Total convidados presentes"],
            var_name="Tipo",
            value_name="Total convidados",
        )
        # Renomeia os valores da coluna 'Tipo' para 'Previsto'/'Presentes'
        df_mes_conv_melt["Tipo"] = df_mes_conv_melt["Tipo"].replace(
            {"Total convidados previsto": "Previsto", "Total convidados presentes": "Presentes"}
        )

        # 2c. Contagem de Eventos (df_mes_contagem)
        # Conta quantos eventos existem para cada Etapa e Local no mês de análise
        df_mes_contagem = (
            df_eventos_mes_analise.groupby(["Etapa", "Local"]).size().reset_index(name="Contagem Etapa")
        ).copy()

        # 3. Melt de Valores Acumulados (df_acumulado_fat_melt) - TODOS os dados
        # Usado para um possível gráfico de evolução ao longo do tempo (não usado no painel final, mas gerado)
        df_acumulado_fat_melt = df_eventos_bruto.melt(
            id_vars=["Ano evento", "Local"],
            value_vars=["Valor total previsto", "Valor total realizado"],
            var_name="Tipo",
            value_name="Valor total acumulado",
        )
        df_acumulado_fat_melt["Tipo"] = df_acumulado_fat_melt["Tipo"].replace(
            {"Valor total previsto": "Previsto", "Valor total realizado": "Realizado"}
        )

        return df_mes_fat_melt, df_mes_conv_melt, df_mes_contagem, df_acumulado_fat_melt


    def _criar_grafico_previsto_realizado(
        self,
        df: pd.DataFrame,
        local: str,
        eixo_y: str,
        titulo_base: str,
        labels: Dict[str, str] = None
    ) -> go.Figure:
        """
        Cria um gráfico de barras Previsto vs. Realizado (ou Presentes) para um local específico.

        :param df: DataFrame de faturamento ou convidados (no formato melted).
        :type df: pd.DataFrame
        :param local: Nome do local a ser filtrado (ex: "Thai house").
        :type local: str
        :param eixo_y: Coluna a ser usada no eixo Y (ex: "Valor total" ou "Total convidados").
        :type eixo_y: str
        :param titulo_base: Parte fixa do título do gráfico (ex: "Total Valor").
        :type titulo_base: str
        :param labels: Dicionário para renomear rótulos.
        :type labels: Dict[str, str], optional
        :returns: O objeto Figure do Plotly (go.Figure/px.bar).
        :rtype: go.Figure
        """
        df_filtrado = df.query(f'Local == "{local}"')
        is_currency = eixo_y == "Valor total"

        # Define a unidade de medida para o título
        unidade = 'R$' if is_currency else 'Pessoas'
        # Define o nome para a comparação (Realizado ou Presente)
        tipo_comparacao = 'Realizado' if is_currency else 'Presente'

        fig = px.bar(
            df_filtrado,
            x="Etapa",
            y=eixo_y,
            color="Tipo", # 'Previsto' ou 'Realizado'/'Presentes'
            labels=labels or {},
            title=f"{local} - {titulo_base} Previsto vs. {tipo_comparacao} ({unidade})",
            text_auto=True,
            barmode="group",
        )
        return fig


    def _criar_grafico_comparativo_eventos(self, df_eventos: pd.DataFrame) -> go.Figure:
        """
        Cria um gráfico de barras para comparar a contagem de eventos por etapa e local.

        :param df_eventos: DataFrame com a contagem de eventos por Etapa e Local.
        :type df_eventos: pd.DataFrame
        :returns: O objeto Figure do Plotly (go.Figure/px.bar).
        :rtype: go.Figure
        """
        fig = px.bar(
            df_eventos,
            x="Etapa",
            y="Contagem Etapa",
            color="Local",
            title="Comparativo de Fechamento de Eventos por Local",
            text_auto=True,
            barmode="group",
            color_discrete_map=self.MAPA_CORES_LOCAL,
        )
        return fig


    def _renomear_traces_e_adicionar(
        self,
        fig_origem: go.Figure,
        fig_destino: go.Figure,
        linha: int,
        coluna: int,
        mostrar_legenda: bool = True
    ):
        """
        Renomeia os traces (usando MAPA_RENOMEACAO_DADOS), gerencia a legenda
        e adiciona os traces a um subplot combinado (go.Figure).

        :param fig_origem: Figura Plotly Express/GO de onde os traces serão copiados.
        :type fig_origem: go.Figure
        :param fig_destino: Objeto go.Figure (make_subplots) que receberá os traces.
        :type fig_destino: go.Figure
        :param linha: Linha do subplot de destino.
        :type linha: int
        :param coluna: Coluna do subplot de destino.
        :type coluna: int
        :param mostrar_legenda: Se True, exibe a legenda do trace.
        :type mostrar_legenda: bool, optional
        """
        for trace in fig_origem.data:
            old_name = trace.name
            trace.showlegend = mostrar_legenda

            # 1. Renomeia o trace (colunas 'Valor total previsto' e 'Valor total realizado')
            if old_name in self.MAPA_RENOMEACAO_DADOS:
                new_name = self.MAPA_RENOMEACAO_DADOS[old_name]
                trace.name = new_name
                # 2. Atualiza o texto do hover (tooltip) para refletir o novo nome
                if trace.hovertemplate:
                    # Substitui o nome original pelo novo nome (ex: "Valor total previsto" por "Previsto")
                    trace.hovertemplate = trace.hovertemplate.replace(old_name, new_name)

            # 3. Adiciona o trace ao subplot na posição desejada
            fig_destino.add_trace(trace, row=linha, col=coluna)


    # =========================================================================
    # MÉTODO PRINCIPAL (Público)
    # =========================================================================

    def gerar_painel(self, df_eventos_bruto: pd.DataFrame) -> go.Figure:
        """
        Gera o painel consolidado (2x3 subplots), processando os dados e
        combinando os 5 gráficos em uma única figura.

        :param df_eventos_bruto: DataFrame contendo os dados brutos dos eventos.
        :type df_eventos_bruto: pd.DataFrame
        :returns: Um objeto go.Figure com o painel de gráficos consolidado (5 gráficos em 6 posições).
        :rtype: go.Figure
        """

        # 1. Geração dos DataFrames de análise a partir dos dados brutos
        df_faturamento, df_convidados, df_eventos_contagem, _ = self._gerar_dataframes_analiticos(df_eventos_bruto)

        # 2. Geração dos Gráficos Individuais (Plotly Express)

        # Gráficos Thai house
        fig_fat_thai = self._criar_grafico_previsto_realizado(
            df_faturamento, "Thai house", "Valor total", "Total Valor", labels=self.MAPA_RENOMEACAO_DADOS
        )
        fig_conv_thai = self._criar_grafico_previsto_realizado(
            df_convidados, "Thai house", "Total convidados", "Total Convidados"
        )

        # Gráficos River
        fig_fat_river = self._criar_grafico_previsto_realizado(
            df_faturamento, "River", "Valor total", "Total Valor"
        )
        fig_conv_river = self._criar_grafico_previsto_realizado(
            df_convidados, "River", "Total convidados", "Total Convidados"
        )

        # Gráfico Comparativo de Eventos (Contagem)
        fig_eventos_comp = self._criar_grafico_comparativo_eventos(df_eventos_contagem)

        # 3. Criação da estrutura de Subplot Combinado (3 linhas x 2 colunas)
        fig_painel = make_subplots(
            rows=3,
            cols=2,
            # Usa os títulos das figuras individuais como títulos dos subplots
            subplot_titles=[
                fig_fat_thai.layout.title.text,
                fig_conv_thai.layout.title.text,
                fig_fat_river.layout.title.text,
                fig_conv_river.layout.title.text,
                fig_eventos_comp.layout.title.text,
                "", # Posição (3, 2) é deixada vazia
            ],
        )

        # 4. Adição e Configuração dos Traces aos Subplots
        # Adiciona os traces e configura a legenda. A legenda só é exibida na primeira ocorrência de cada 'Tipo'
        self._renomear_traces_e_adicionar(fig_fat_thai, fig_painel, 1, 1, mostrar_legenda=True)
        self._renomear_traces_e_adicionar(fig_conv_thai, fig_painel, 1, 2, mostrar_legenda=False) # Legenda de convidados é a mesma de faturamento
        self._renomear_traces_e_adicionar(fig_fat_river, fig_painel, 2, 1, mostrar_legenda=False)
        self._renomear_traces_e_adicionar(fig_conv_river, fig_painel, 2, 2, mostrar_legenda=False)
        self._renomear_traces_e_adicionar(fig_eventos_comp, fig_painel, 3, 1, mostrar_legenda=True) # Legenda de Local

        # 5. Atualização Final do Layout
        fig_painel.update_layout(
            title={"text": self.titulo_geral, "x": 0.5, "xanchor": "center"},
            font=dict(size=12),
            height=1200,
            width=1400,
            showlegend=True,
            barmode="group",
        )

        # 6. Ajuste de Títulos e Formatação dos Eixos Y
        fig_painel.update_yaxes(title_text="Valor Total (R$)", row=1, col=1)
        fig_painel.update_yaxes(title_text="Valor Total (R$)", row=2, col=1)
        fig_painel.update_yaxes(title_text="Total Convidados", row=1, col=2)
        fig_painel.update_yaxes(title_text="Total Convidados", row=2, col=2)
        fig_painel.update_yaxes(title_text="Contagem de Eventos", row=3, col=1)
        fig_painel.update_xaxes(title_text="Etapa", row=3, col=1) # Adiciona o rótulo do Eixo X

        return fig_painel


# =========================================================================
# CLASSE: RELATÓRIO DE EVENTOS POR FAIXA DE CONVIDADOS
# =========================================================================

class GeradorRelatoriosEventos:
    """
    Classe para gerar e exibir um relatório visual consolidado (subplots 2x2)
    de eventos realizados, focando na distribuição da Contagem e Faturamento
    em relação ao número de Convidados Presentes (histogramas binned).
    """

    def __init__(self, df: pd.DataFrame, ano_referencia: int, local_analisado: str = 'Thai house'):
        """
        Inicializa o gerador de relatórios com os dados e parâmetros de análise.

        :param df: DataFrame contendo os dados dos eventos.
        :type df: pd.DataFrame
        :param ano_referencia: O ano que será usado no título do relatório (para referência).
        :type ano_referencia: int
        :param local_analisado: O nome do local para filtrar. Padrão é 'Thai house'.
        :type local_analisado: str, optional
        """
        self.df_dados = df
        self.ano_referencia = ano_referencia
        self.local_analisado = local_analisado
        # Variáveis para armazenar as figuras individuais antes de combiná-las
        self.figura_contagem = None
        self.figura_percentual_contagem = None
        self.figura_faturamento = None
        self.figura_percentual_faturamento = None


    def _filtrar_dados(self) -> pd.DataFrame:
        """
        Aplica o filtro base nos dados: eventos 'Realizados', com valores > 0
        para faturamento e convidados, e filtrado pelo 'Local' de análise.

        :returns: O DataFrame filtrado.
        :rtype: pd.DataFrame
        """
        # Condição de filtro aplicada aos dados
        filtro_base = (
            (self.df_dados['Valor total realizado'] > 0) &
            (self.df_dados['Etapa'] == 'Realizado') &
            (self.df_dados['Total convidados presentes'] > 0) &
            (self.df_dados['Local'] == self.local_analisado) &
            (self.df_dados['Data evento'].dt.year == self.ano_referencia)
        )
        return self.df_dados.query('@filtro_base')


    def _criar_histograma(
        self,
        df_filtrado: pd.DataFrame,
        titulo: str,
        coluna_y: str = None,
        tipo_normalizacao: str = None,
        cor: str = "darkolivegreen",
        formato_texto: str = "%{y:,.0f}"
    ) -> px.histogram:
        """
        Cria um histograma Plotly Express com configurações padronizadas (10 bins e texto auto).

        O eixo X é sempre 'Total convidados presentes'.

        :param df_filtrado: DataFrame já filtrado para o gráfico.
        :type df_filtrado: pd.DataFrame
        :param titulo: Título do gráfico (será usado no subplot).
        :type titulo: str
        :param coluna_y: Coluna a ser mapeada para o eixo Y. Se None, é contagem (padrão).
        :type coluna_y: str, optional
        :param tipo_normalizacao: Tipo de normalização ('percent' ou None).
        :type tipo_normalizacao: str, optional
        :param cor: Cor das barras.
        :type cor: str, optional
        :param formato_texto: String de formatação para os textos das barras.
        :type formato_texto: str, optional
        :returns: O objeto Figure do Plotly.
        :rtype: px.histogram
        """
        fig = px.histogram(
            df_filtrado,
            x="Total convidados presentes", # Eixo X é sempre o número de convidados
            y=coluna_y,
            text_auto=True,
            barmode="relative",
            nbins=10, # Cria 10 faixas (bins) de convidados
            histnorm=tipo_normalizacao,
            color_discrete_sequence=[cor],
        )

        # Atualizações de layout e traces para padronizar o visual
        _ = fig.update_layout(
            title_font_size=18,
            bargap=0.1,
            separators=",.",
            title_text=titulo # Título usado para o subplot
        )
        _ = fig.update_traces(texttemplate=formato_texto)

        return fig


    def criar_figuras_histograma(self):
        """
        Cria as quatro figuras de histograma individuais:
        1. Contagem Absoluta
        2. Contagem Percentual
        3. Faturamento Absoluto
        4. Faturamento Percentual
        """
        # Aplica o filtro base uma única vez
        df_eventos_filtrados = self._filtrar_dados()

        # 1. Contagem de Eventos (Valor Absoluto)
        self.figura_contagem = self._criar_histograma(
            df_eventos_filtrados,
            "Contagem de Eventos por Número de Convidados",
            coluna_y=None,
            tipo_normalizacao=None,
            cor="darkolivegreen",
            formato_texto="%{y:,.0f}"
        )

        # 2. Contagem de Eventos (Percentual)
        self.figura_percentual_contagem = self._criar_histograma(
            df_eventos_filtrados,
            "Percentual de Eventos por Número de Convidados",
            coluna_y=None,
            tipo_normalizacao="percent", # Normaliza a contagem para percentual
            cor="darkolivegreen",
            formato_texto="%{y:,.2f}%"
        )

        # 3. Faturamento (Valor Absoluto)
        self.figura_faturamento = self._criar_histograma(
            df_eventos_filtrados,
            "Acumulado do Faturamento por Número de Convidados",
            coluna_y='Valor total realizado',
            tipo_normalizacao=None,
            cor="darkslategrey",
            formato_texto="%{y:,.0f}"
        )

        # 4. Faturamento (Percentual)
        self.figura_percentual_faturamento = self._criar_histograma(
            df_eventos_filtrados,
            "Percentual do Faturamento por Número de Convidados",
            coluna_y='Valor total realizado',
            tipo_normalizacao="percent", # Normaliza o faturamento para percentual
            cor="darkslategrey",
            formato_texto="%{y:,.2f}%"
        )


    def criar_subplots_combinados(self) -> go.Figure:
        """
        Combina as quatro figuras individuais (criadas em 'criar_figuras_histograma')
        em um único objeto de subplots (2 linhas x 2 colunas).

        :returns: A figura Plotly com os 4 subplots combinados.
        :rtype: go.Figure
        """
        # Garante que as figuras foram criadas
        if any(f is None for f in [self.figura_contagem, self.figura_percentual_contagem, self.figura_faturamento, self.figura_percentual_faturamento]):
            self.criar_figuras_histograma()

        # Nomes dos títulos de cada subplot (usando os títulos definidos nos histogramas)
        titulos_subplots = [
            self.figura_contagem.layout.title.text,
            self.figura_percentual_contagem.layout.title.text,
            self.figura_faturamento.layout.title.text,
            self.figura_percentual_faturamento.layout.title.text
        ]

        # Cria a estrutura de subplots 2x2
        fig_subplots = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=titulos_subplots,
        )

        # Adiciona cada trace (gráfico) ao seu respectivo lugar no subplot
        # O método append_trace é usado para transferir traces de Plotly Express para subplots
        fig_subplots.append_trace(self.figura_contagem.data[0], row=1, col=1)
        fig_subplots.append_trace(self.figura_percentual_contagem.data[0], row=1, col=2)
        fig_subplots.append_trace(self.figura_faturamento.data[0], row=2, col=1)
        fig_subplots.append_trace(self.figura_percentual_faturamento.data[0], row=2, col=2)

        # Configurações globais do layout do subplot
        fig_subplots.update_layout(
            height=1000,
            width=1400,
            # title_text=f"Distribuição de Eventos Realizados - {self.local_analisado} (Ano {self.ano_referencia})",
            title_text="",
            bargap=0.1,
            title_x=0.5,
        )

        # Configura o Título do Eixo X para todos os subplots
        fig_subplots.update_xaxes(title_text="Total convidados presentes", row=1, col=1)
        fig_subplots.update_xaxes(title_text="Total convidados presentes", row=1, col=2)
        fig_subplots.update_xaxes(title_text="Total convidados presentes", row=2, col=1)
        fig_subplots.update_xaxes(title_text="Total convidados presentes", row=2, col=2)

        # Configura o Título e Formatação do Eixo Y para cada subplot
        fig_subplots.update_yaxes(title_text="Contagem Absoluta", row=1, col=1, showticklabels=False)
        fig_subplots.update_yaxes(title_text="Contagem (%)", row=1, col=2, tickformat=".0%", showticklabels=False)
        fig_subplots.update_yaxes(title_text="Faturamento Absoluto (R$)", row=2, col=1, tickprefix="R$", showticklabels=False)
        fig_subplots.update_yaxes(title_text="Faturamento (%)", row=2, col=2, tickformat=".0%", showticklabels=False)

        return fig_subplots


    def gerar_relatorio_completo(self) -> go.Figure:
            """
            Executa a sequência completa para criar e retornar o relatório consolidado 2x2.

            :returns: A figura Plotly do relatório consolidado.
            :rtype: go.Figure
            """
            print(f"Gerando relatório para o local: {self.local_analisado} (Ano {self.ano_referencia})...")
            self.criar_figuras_histograma()
            # Retorna a figura combinada
            summary_plot = self.criar_subplots_combinados()
            print("Relatório gerado e exibido com sucesso.")

            return summary_plot