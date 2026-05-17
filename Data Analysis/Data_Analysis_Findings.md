# Exploratory Data Analysis: Motor Predictive Maintenance
**Project:** Predictive Maintenance for Electrical Machines - II
**Dataset:** `motor_pdm_final_dataset.csv` (and cleaned version `motor_pdm_fruitful.csv`)
**Total Samples:** 600 target readings

This report details the findings from the synthetic motor condition monitoring dataset. The dataset contains healthy baseline operations along with three unique fault modes. Below is an examination of summary statistics, data quality, and signature visual characteristics of each failure state.

---

## 1. Summary Statistics Breakdown

The sensory readings natively separate across the four designated class condition labels: 
- `0`: Healthy
- `1`: Unbalanced Load
- `2`: Overheat
- `3`: Bearing Fault

**Current (A)**
- **Healthy (`0`)**: Mean 1.34A ± 0.36
- **Unbalanced (`1`)**: Mean 1.73A ± 0.11 (Reflects precisely the 15% programmed increase baseline scaling)
- **Overheat (`2`)**: Mean 1.49A ± 0.10
- **Bearing Fault (`3`)**: Mean 1.86A ± 0.88 (The very high Standard Deviation is indicative of the intermittent fast 2.5A current spiking behavior).

**VFD Temp (°C)**
- **Healthy (`0`)**: Mean 49.3°C ± 11.8
- **Unbalanced (`1`)**: Mean 45.0°C ± 4.5
- **Overheat (`2`)**: Mean 95.3°C ± 5.4 (Critical overheating range far beyond nominal conditions)
- **Bearing Fault (`3`)**: Mean 45.3°C ± 5.3

**Cooling Efficiency (C/VA)**
- **Healthy (`0`)**: ~0.12 (Nominal cooling ratio)
- **Overheat (`2`)**: ~0.04 (This dramatic plunge highlights the massive operational inefficiency during overheating episodes).

---

## 2. Correlation Analysis

The correlation heatmap maps out relationships between variables across all structural states:

![Correlation Heatmap](./correlation_heatmap.png)

**Key Takeaways:**
1. There is an obvious near-perfect positive correlation (1.00) between `Frequency(Hz)` and `RPM`, validating foundational electrical relations.
2. `State_Label` correlates negatively with `CoolingEfficiency` (-0.46) and slightly positively with `Current(A)` (0.33) pointing to the strongest features to help a predictive model determine faults.

---

## 3. Distribution Visualizations

Box plots emphasize interquartile ranges and bounds distribution across distinct fault profiles. 

![Box Plots](./box_plots.png)

- **Current(A)**: Notice how Unbalanced Load shifts the entire interquartile bounds distribution upward compared to Healthy, while Bearing Fault generates massive positive outliers stretching up to >4.0A representing erratic spikes.
- **VFD_Temp(C)**: Shows the extremely rigid class boundary for the Overheating condition compared to normal operations. An algorithm could easily spot this class condition almost purely on this separation.
- **RPM**: Fading class correlation; essentially identical across states.

---

## 4. Fault Signature Analysis

Plotting explicit variable interactions visually clusters the features together like fingerprint classification patterns.

![Signature Scatter Plots](./signature_analysis.png)

- **Frequency vs Current**: Bearing Fault points scatter densely yet distinctly as massive independent outliers over the top of the linearly scaling sequence line representing Healthy. Unbalanced Load simply traces a similarly linear but displaced and elevated trend line above the normal load.
- **Frequency vs Temp**: Returns a stark, impenetrable band of overheating operations strictly isolated across all frequency structures. Forms a highly distinct classification line independent of machine speed.

---

## 5. Data Quality & Preprocessing Actions taken

- **Missing Values**: Handled natively (0 missing/NaN elements discovered).
- **Quality Check (Outliers)**: Found exactly **8** IQR-calculated outliers universally within "Healthy" current readings. These predictably originate during low-frequency initial motor startup current pulls. No intervention is needed as these are genuine operational realities.
- **Data Cleanup**: As part of preparing for an ML training pipeline, `motor_pdm_fruitful.csv` was cleanly stripped of all irrelevant components (like human-timestamp tracking) that interfere with feature learning blocks. 
