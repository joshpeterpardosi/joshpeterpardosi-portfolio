# 🌐 Josh Peter Pardosi — Data Analyst Portfolio

> A personal portfolio website presenting my data analysis and forecasting work, with results and their limitations stated openly.

<p align="center">
<a href="https://joshpeterpardosi.github.io/joshpeterpardosi-portfolio/">
<img src="https://img.shields.io/badge/Visit_Live_Portfolio-2563EB?style=for-the-badge" alt="Live Portfolio" />
</a>
</p>

---

## 📂 Projects Featured

| Project | Focus | Tools |
|---------|-------|-------|
| **MLOps Pipeline — Churn Prediction & Revenue Forecasting** | Dagster-orchestrated churn + MRR forecasting loop with MLflow promotion, FastAPI serving, and Evidently-triggered retraining; 107 tests; 0.80 churn recall at a cost-chosen threshold (0.84 ROC-AUC) | Python, Dagster, MLflow, LightGBM, FastAPI, Evidently, Docker |
| **E-Commerce Conversion Funnel & Customer Retention** | Funnel, cohort retention, and RFM segmentation over 507,928 clickstream events on DuckDB/Parquet; 11 tests, live Streamlit dashboard | DuckDB, Python, Parquet, Streamlit, Plotly, Pytest |
| **Data Quality & Observability Platform** | Five-dimension validation gate curating messy e-commerce CSVs into a clean, audited dataset; 20 tests | Python, DuckDB, Pandera, Streamlit, Plotly, Pytest |
| **Real-Time Event Pipeline — Fraud/Transaction Detection** | Kafka-streamed transactions, rule-based + ML fraud scoring (0.856 precision / 0.786 recall, past a 0.80 / 0.70 release gate), ClickHouse storage, dual Grafana/Streamlit dashboards; 49 tests | Kafka (Redpanda), Python, ClickHouse, Grafana, Streamlit |

### Also worth a look

| Project | Focus | Tools |
|---------|-------|-------|
| **A/B Testing — Marketing Campaign** | Experiment analysis on 588,101 users; 43% conversion lift verified as timing-independent | Python, Pandas, SciPy, statsmodels |
| **E-Commerce ELT Pipeline & Review Score Prediction** | dbt/BigQuery ELT over the Olist dataset feeding a review-score prediction model | Python, dbt, BigQuery, scikit-learn |

---

## 🛠️ Built With

| Technology | Purpose |
|------------|---------|
| **HTML5** | Page structure and semantic markup |
| **CSS3** | Layout, typography, and responsive design (`assets/site.css`) |
| **GitHub Pages** | Static hosting directly from this repository |

No frameworks, no JavaScript, and no build step — `index.html`, a case study page in `work/`, and an `assets/` folder.

---

## 🚀 Running Locally
