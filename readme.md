# UAC Care Pipeline Analysis
### Care Transition Efficiency & Placement Outcome Analytics
**Organization:** U.S. Department of Health and Human Services (HHS) — Unified Mentor Program

---

## 📌 Project Overview

This project reframes the UAC (Unaccompanied Alien Children) dataset from a capacity monitoring lens to a **process efficiency and outcome evaluation lens**.

By analyzing how effectively children move through the care pipeline, it provides actionable insights for improving reunification timelines, reducing delays, and strengthening child welfare outcomes.

---

## 🔄 Care Pipeline Stages

```
Apprehension → CBP Custody → HHS Care → Sponsor Placement (Discharge)
```

| Stage | Description |
|---|---|
| CBP Custody | Initial holding after apprehension |
| HHS Care | Medical screening, sheltering, case management |
| Sponsor Placement | Discharge and reunification with vetted sponsor |

---

## 📁 Project Structure

```
uac-care-pipeline/
│
├── data/
│   └── HHS_Unaccompanied_Alien_Children_Program.csv
│
├── notebooks/
│   └── uac_care_pipeline_analysis.ipynb
│
├── app/
│   └── app.py                  ← Streamlit Dashboard
│
├── reports/
│   └── report.md               ← Research Paper / EDA Report
│
├── requirements.txt
└── README.md
```

---

## 📊 KPIs Analyzed

| KPI | Formula | Description |
|---|---|---|
| Transfer Efficiency Ratio | Transfers ÷ CBP Custody | CBP → HHS speed |
| Discharge Effectiveness | Discharges ÷ HHS Care | Placement success rate |
| Pipeline Throughput Rate | Discharges ÷ Apprehensions | Overall system movement |
| Backlog Accumulation Rate | Apprehensions − Discharges | Delay severity |
| Outcome Stability Score | 7-day Rolling Std Dev | Consistency of placements |

---

## 🚀 How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Jupyter Notebook
```bash
jupyter notebook notebooks/uac_care_pipeline_analysis.ipynb
```

### 3. Run Streamlit Dashboard
```bash
streamlit run app/app.py
```

---

## 🔍 Key Findings

- **Transfer Efficiency (~69%)** — Children move from CBP to HHS at a moderate rate
- **Discharge Effectiveness (~2%)** — Major bottleneck at HHS stage; very low placement rate
- **2025 Sharp Decline** — Significant drop in both inflow and outflow suggesting systemic shift
- **Weekend throughput slightly higher** than weekday throughput
- **Prolonged stagnation in 2025** — discharge effectiveness consistently low with no recovery

---

## 📦 Deliverables

- ✅ Jupyter Notebook (EDA + KPI Analysis)
- ✅ Streamlit Dashboard (Live Analytics)
- ✅ Research Report (Insights + Recommendations)
- ✅ README (Project Documentation)
- ✅ Requirements.txt

---

## 👤 Author

**Unified Mentor Internship Project**
U.S. Department of Health and Human Services