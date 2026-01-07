## 📄 README.md

## Análise e Gestão de Eventos 📊

Este projeto consiste em um dashboard interativo desenvolvido com **Streamlit** e **Plotly** para a análise e gestão de eventos. O objetivo é fornecer uma visão abrangente sobre o desempenho financeiro, a demanda e as estatísticas operacionais de eventos, com foco em comparação entre diferentes locais e períodos.

**⚠️ Aviso Importante:** O conjunto de dados utilizado neste dashboard é **fictício**, criado para simular dados de eventos reais (`Thai house` e `River`). O projeto foi desenvolvido com o propósito de **portfólio**, demonstrando habilidades em Engenharia de Dados (ETL), Análise de Dados e Desenvolvimento de Aplicações Web interativas (Streamlit).

---

### 🚀 Funcionalidades Principais

O dashboard é estruturado em abas para facilitar a navegação e a análise aprofundada:

1. **💰 Visão Financeira:** Acompanhamento da evolução histórica e mensal dos valores **Previstos** e **Realizados**, além da análise do **Ticket Médio** por local.
2. **📈 Análise de Demanda & Frequência:** Gráficos de frequência e distribuição do volume de **Orçamentos** e **Convidados**, segmentados por ano, mês, dia da semana, etapa e tipo de cardápio.
3. **📋 Detalhamento & Estatísticas:** Tabelas com **Estatísticas Descritivas** (média, desvio padrão, min/max) de métricas financeiras e de convidados, e tabelas detalhadas dos eventos por status (Negociação, Fechado, Realizado).
4. **Relatórios Executivos (KPIs):** Painéis de resumo comparativo de performance (mês a mês), e relatórios executivos detalhados para cada local.

---

### ⚙️ Explicações Técnicas e Arquitetura

O projeto utiliza uma arquitetura modularizada em Python, focada em clareza, reusabilidade e performance:

#### 1. Estrutura de Pastas (Presumida)

O código `app.py` depende de módulos seguindo as melhores práticas de Engenharia de Dados:

* **`app.py`**: Arquivo principal do Streamlit, responsável pela interface e visualização.
* **`etl_preprocessor.py`**: Contém a função `run_full_etl` para a extração, transformação e carregamento (ETL) dos dados brutos.
* **`etl_utils.py`**: Contém classes auxiliares como `DataProcess` (pré-processamento), `FilterSelection` (aplicação de filtros) e `dre` (funções de demonstração de resultado, possivelmente).
* **`charts.py`**: Contém as funções de plotagem (`config_plot`, `plot_hist`, `plot_pie`, `plot_hztl`, `create_table`, `PainelEventos`, `GeradorRelatoriosEventos`), responsáveis pela criação e configuração dos gráficos Plotly.

#### 2. Processamento e Otimização

* **ETL (Extração, Transformação e Carga):** O `df = run_full_etl(...)` é o ponto de partida. A função carrega os dados brutos e realiza as transformações necessárias para que o DataFrame (`df`) esteja pronto para a análise.
* **Cache de Dados (`@st.cache_data`):** A função `load_data()` é decorada com `@st.cache_data` do Streamlit. Isso garante que o processo de ETL completo (`run_full_etl`) seja executado apenas na primeira vez ou quando o código subjacente for alterado, **otimizando drasticamente o tempo de carregamento** do dashboard para os usuários.
* **Pré-processamento e Filtragem:** A classe `DataProcess` garante a limpeza e formatação inicial, e a filtragem inicial restringe os dados para eventos a partir de 2022 (`.query('`Ano evento` > 2021')`).
* **Personalização de Gráficos:** A biblioteca **Plotly** é usada com configurações padrão (`plotly_white`) e escalas de cores personalizadas, garantindo uma estética limpa e consistente em todo o dashboard.

#### 3. Interação do Usuário (Streamlit Sidebar)

A barra lateral (`st.sidebar`) é utilizada para os principais filtros, garantindo que o usuário possa interagir e segmentar a análise rapidamente:

* **Seleção de Local:** Permite selecionar um ou mais locais (e.g., `Thai house`, `River`).
* **Seleção de Ano:** Permite focar a análise em um ano específico (o ano atual é o padrão).
* **Seleção de Etapa:** Permite filtrar eventos por status (e.g., Orçamento, Negociação, Realizado).

---

### 💻 Como Executar o Projeto Localmente

#### Pré-requisitos

Certifique-se de ter o Python instalado. O projeto requer as seguintes bibliotecas principais, além dos módulos locais (que você precisará criar ou simular):

* `streamlit`
* `pandas`
* `numpy`
* `plotly`
* `dateutil`

#### 1. Instalação das Dependências

Crie um ambiente virtual e instale as dependências. Você pode usar um arquivo `requirements.txt` (não fornecido, mas recomendado).

```bash
pip install streamlit pandas numpy plotly "python-dateutil"

```

#### 2. Estrutura Mínima para Execução

Para rodar `app.py`, você **deve** criar os arquivos `etl_preprocessor.py`, `etl_utils.py` e `charts.py` e simular as classes/funções necessárias (como `run_full_etl`, `DataProcess`, `FilterSelection`, `plot_hist`, etc.) que retornem DataFrames ou objetos Plotly válidos, mesmo que com dados simulados/vazios, para evitar erros de importação.

#### 3. Execução do Dashboard

Com os arquivos de módulos auxiliares criados/simulados, execute o dashboard via Streamlit:

```bash
streamlit run app.py

```

O dashboard será aberto automaticamente em seu navegador padrão.

---

### 💡 Próximos Passos (Desenvolvimento Futuro)

1. **Implementação do Funil de Conversão:** Completar a aba de **Conversão** (atualmente comentada) com métricas e um gráfico de funil (requer a implementação de métricas de funil na camada ETL/Utils).
2. **Integração de Banco de Dados:** Migrar a fonte de dados de planilhas/arquivos locais para um Banco de Dados robusto (PostgreSQL, MySQL, etc.) para melhor escalabilidade e integridade.
3. **Alertas de Performance:** Adicionar lógica para notificar o usuário (via Streamlit info/warning boxes) quando KPIs importantes estiverem fora da meta.