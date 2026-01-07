## 📄 README.md

## Event Analysis and Management 📊

This project is an interactive dashboard developed with **Streamlit** and **Plotly** for event analysis and management. The objective is to provide a comprehensive view of the financial performance, demand, and operational statistics of events, focusing on comparisons between different venues and periods.

**⚠️ Important Notice:** The dataset used in this dashboard is **fictitious**, created to simulate real event data (`Thai house` and `River`). The project was developed for **portfolio purposes**, demonstrating skills in Data Engineering (ETL), Data Analysis, and Interactive Web Application Development (Streamlit).

---

### 🚀 Key Features

The dashboard is structured into tabs to facilitate navigation and in-depth analysis:

1. **💰 Financial View:** Tracking the historical and monthly evolution of **Forecasted** and **Actual** values, in addition to the analysis of the **Average Ticket** per venue.
2. **📈 Demand & Frequency Analysis:** Frequency and distribution charts for the volume of **Quotes** and **Guests**, segmented by year, month, day of the week, stage, and menu type.
3. **📋 Detailing & Statistics:** Tables with **Descriptive Statistics** (mean, standard deviation, min/max) for financial and guest metrics, and detailed tables of events by status (Negotiation, Closed, Actualized).
4. **Executive Reports (KPIs):** Comparative summary performance panels (month-over-month), and detailed executive reports for each venue.

---

### ⚙️ Technical Explanations and Architecture

The project uses a modularized architecture in Python, focused on clarity, reusability, and performance:

#### 1. (Assumed) Folder Structure

The `app.py` code depends on modules following data engineering best practices:

* **`app.py`**: The main Streamlit file, responsible for the interface and visualization.
* **`etl_preprocessor.py`**: Contains the `run_full_etl` function for the extraction, transformation, and loading (ETL) of raw data.
* **`etl_utils.py`**: Contains helper classes such as `DataProcess` (pre-processing), `FilterSelection` (filter application), and `dre` (demonstration of results functions, possibly).
* **`charts.py`**: Contains the plotting functions (`config_plot`, `plot_hist`, `plot_pie`, `plot_hztl`, `create_table`, `PainelEventos`, `GeradorRelatoriosEventos`), responsible for creating and configuring the Plotly charts.

#### 2. Processing and Optimization

* **ETL (Extract, Transform, and Load):** `df = run_full_etl(...)` is the starting point. The function loads the raw data and performs the necessary transformations so that the DataFrame (`df`) is ready for analysis.
* **Data Caching (`@st.cache_data`):** The `load_data()` function is decorated with Streamlit's `@st.cache_data`. This ensures that the complete ETL process (`run_full_etl`) is executed only the first time or when the underlying code is changed, **drastically optimizing the dashboard loading time** for users.
* **Pre-processing and Filtering:** The `DataProcess` class ensures initial cleaning and formatting, and the initial filtering restricts the data to events from 2022 onwards (`.query('`Ano evento` > 2021')`).
* **Chart Customization:** The **Plotly** library is used with default settings (`plotly_white`) and customized color scales, ensuring a clean and consistent aesthetic throughout the dashboard.

#### 3. User Interaction (Streamlit Sidebar)

The sidebar (`st.sidebar`) is used for the main filters, ensuring the user can interact and segment the analysis quickly:

* **Venue Selection:** Allows selecting one or more venues (e.g., `Thai house`, `River`).
* **Year Selection:** Allows focusing the analysis on a specific year (the current year is the default).
* **Stage Selection:** Allows filtering events by status (e.g., Quote, Negotiation, Actualized).

---

### 💻 How to Run the Project Locally

#### Prerequisites

Ensure you have Python installed. The project requires the following main libraries, in addition to the local modules (which you will need to create or simulate):

* `streamlit`
* `pandas`
* `numpy`
* `plotly`
* `dateutil`

#### 1. Installing Dependencies

Create a virtual environment and install the dependencies. You can use a `requirements.txt` file (not provided, but recommended).

```bash
pip install streamlit pandas numpy plotly "python-dateutil"

```

#### 2. Minimum Execution Structure

To run `app.py`, you **must** create the files `etl_preprocessor.py`, `etl_utils.py`, and `charts.py` and simulate the necessary classes/functions (such as `run_full_etl`, `DataProcess`, `FilterSelection`, `plot_hist`, etc.) that return valid DataFrames or Plotly objects, even if with simulated/empty data, to avoid import errors.

#### 3. Running the Dashboard

With the auxiliary module files created/simulated, run the dashboard via Streamlit:

```bash
streamlit run app.py

```

The dashboard will automatically open in your default browser.

---

### 💡 Next Steps (Future Development)

1. **Conversion Funnel Implementation:** Complete the **Conversion** tab (currently commented out) with metrics and a funnel chart (requires the implementation of funnel metrics in the ETL/Utils layer).
2. **Database Integration:** Migrate the data source from spreadsheets/local files to a robust Database (PostgreSQL, MySQL, etc.) for better scalability and integrity.
3. **Performance Alerts:** Add logic to notify the user ( via Streamlit info/warning boxes) when important KPIs are off-target.