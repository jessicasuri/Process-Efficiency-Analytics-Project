# UAC Care Pipeline — Research Report
### Care Transition Efficiency & Placement Outcome Analytics

**Organization:** U.S. Department of Health and Human Services (HHS)
**Program:** Unified Mentor Internship
**Dataset:** HHS Unaccompanied Alien Children Program

---

## 1. Executive Summary

This report analyzes the operational efficiency of the Unaccompanied Alien Children (UAC) care pipeline managed by the U.S. Department of Health and Human Services (HHS). Using daily operational data, key performance indicators were derived to evaluate transition speed, discharge outcomes, backlog formation, and placement stability.

The analysis reveals a **critical bottleneck at the HHS discharge stage**, with placement success rates as low as ~2%, despite moderate transfer efficiency (~69%) from CBP custody. A significant system-wide decline is observed in 2025, pointing to structural challenges in the final stage of the reunification pipeline.

---

## 2. Problem Statement

While aggregate counts of children in custody are routinely monitored, **process efficiency metrics are largely absent** from standard reporting. Key unanswered questions include:

- How efficiently are children transferred from CBP to HHS?
- Are discharges keeping pace with inflows?
- When and where do care backlogs accumulate?
- Are placement outcomes improving or deteriorating over time?

Without structured transition analytics, system bottlenecks remain hidden and policy interventions are poorly targeted.

---

## 3. Dataset Description

| Column | Description |
|---|---|
| Date | Reporting date |
| cbp_apprehended | Daily intake — children apprehended and placed in CBP custody |
| cbp_custody | Active CBP care load |
| cbp_transferred | Children transferred out of CBP to HHS |
| hhs_care | Active HHS care load |
| hhs_discharged | Children discharged from HHS to sponsor placement |

**Data Cleaning Steps:**
- Removed duplicate rows to prevent double-counting
- Dropped rows with all-null values to protect data integrity
- Sorted chronologically by Date for time-series accuracy
- Converted `hhs_care` from object to float (comma-separated strings)
- Renamed all columns to snake_case for consistency

---

## 4. Exploratory Data Analysis (EDA)

### 4.1 CBP Custody Trend
CBP custody levels increased steadily over time, peaking around 2024. A sharp decline in 2025 suggests either improved transfer efficiency or a reduction in overall apprehensions.

### 4.2 HHS Care Trend
HHS care load peaked around late 2023 and throughout 2024, indicating growing backlog in processing and placement. The 2025 decline mirrors CBP trends, suggesting system-wide activity reduction.

### 4.3 Inflow vs Outflow
During 2023–early 2024, outflow (discharges) consistently exceeded inflow (apprehensions), indicating strong throughput. By mid-2024, the gap narrowed significantly. Post-2025, both declined sharply — suggesting the reduction in backlog was driven by **lower inflow** rather than improved discharge capacity.

---

## 5. KPI Analysis

### 5.1 Transfer Efficiency Ratio
**Formula:** CBP Transferred ÷ CBP Custody
**Average:** ~69%

Transfer efficiency shows significant fluctuations but remains at a moderate level overall. A declining trend in the later period indicates worsening CBP → HHS movement speed.

### 5.2 Discharge Effectiveness
**Formula:** HHS Discharged ÷ HHS Care
**Average:** ~2%

This is the most critical KPI. Discharge effectiveness is consistently and extremely low, meaning only ~2% of children in HHS care are placed with sponsors on any given day. A sharp drop in early 2025 indicates a near-complete stall in reunification.

### 5.3 Pipeline Throughput Rate
**Formula:** HHS Discharged ÷ CBP Apprehended

Daily throughput shows high variability with occasional spikes (backlog clearance events). Most periods show throughput below 1.0, meaning outflow lags behind inflow.

### 5.4 Backlog Accumulation Rate
**Formula:** Apprehensions − Discharges

Daily backlog values are predominantly negative (discharges > apprehensions historically), but trend toward zero in 2025, indicating stagnation rather than resolution.

### 5.5 Outcome Stability Score
**Formula:** 7-day Rolling Standard Deviation of Discharge Effectiveness

High variability in the rolling std dev confirms that placement outcomes are **inconsistent and unreliable**. No sustained period of stable high performance is observed.

---

## 6. Bottleneck Detection

The comparison of Transfer Efficiency (~69%) vs. Discharge Effectiveness (~2%) clearly identifies the **HHS discharge stage as the primary bottleneck**.

Children are entering HHS care at a reasonable rate but are not exiting to sponsors efficiently. This points to systemic issues in:
- Sponsor vetting and approval delays
- Case management capacity constraints
- Policy and legal barriers to placement

---

## 7. Temporal & Pattern Analysis

### 7.1 Weekday vs Weekend
Weekend throughput is slightly higher than weekday throughput. This may suggest reduced administrative bottlenecks on weekends or batch processing effects.

### 7.2 Month-over-Month Trends
Discharge effectiveness shows a clear declining trend throughout 2024, with a sharp drop in early 2025. No recovery is observed in the later period, indicating **prolonged stagnation**.

### 7.3 Stagnation Period
2025 represents a prolonged stagnation period — discharge effectiveness remains flat at near-zero with minimal variation. The system has reached a performance plateau at an unacceptably low efficiency level.

---

## 8. Key Findings Summary

| Finding | Detail |
|---|---|
| Primary Bottleneck | HHS discharge stage — only ~2% effectiveness |
| Transfer Performance | Moderate at ~69% but declining |
| 2025 System Shift | Sharp decline in both inflow and outflow |
| Backlog Status | Reducing but driven by lower inflow, not better efficiency |
| Outcome Consistency | Highly variable — no sustained stable performance |
| Weekend Effect | Slightly higher throughput on weekends |

---

## 9. Recommendations

1. **Accelerate sponsor vetting processes** — The biggest delay is at the discharge stage. Streamlining background checks and approval workflows could significantly improve placement rates.

2. **Increase HHS case management capacity** — Adding case workers during peak periods could reduce average time-in-care.

3. **Implement threshold-based monitoring** — Automated alerts when discharge effectiveness falls below a defined threshold (e.g., 1.5%) can trigger early intervention.

4. **Investigate the 2025 decline** — The sharp simultaneous drop in inflow and outflow needs policy-level investigation to understand whether this reflects improved enforcement, reduced migration, or administrative changes.

5. **Weekend processing model** — Since weekends show slightly higher throughput, extending certain processing operations to weekends may improve overall pipeline speed.

6. **Pipeline flow dashboards** — Real-time visibility into each stage of the pipeline for administrators would enable faster decision-making.

---

## 10. Conclusion

The UAC care pipeline analysis reveals that while the system demonstrates moderate capability in moving children from CBP to HHS custody, it **critically underperforms in the final placement stage**. With discharge effectiveness consistently near 2%, thousands of children remain in HHS care far longer than necessary.

Addressing the HHS discharge bottleneck through process reforms, capacity expansion, and real-time monitoring is essential for improving reunification outcomes and upholding the welfare of unaccompanied children.
