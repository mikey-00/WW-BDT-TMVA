# WW-BDT-TMVA
Multivariate BDT analysis for WW signal vs top backgrounds using ROOT TMVA

# WW Signal vs Top Background Discrimination using BDT (TMVA)

This repository contains a multivariate analysis using Boosted Decision Trees (BDTs)
to separate WW signal events from dominant top-quark backgrounds.

## 🔬 Analysis Overview
- Framework: ROOT TMVA
- Classifier: Gradient Boosted Decision Tree
- Signal: WW
- Backgrounds: ttbar, tW, t̄W
- Final observable: BDT score

## 📊 Input Variables
- Lepton transverse momenta (pt1, pt2)
- Lepton pseudorapidities
- Dilepton invariant mass (mll)
- Dilepton transverse momentum (ptll)
- Δφ between leptons
- Missing transverse energy
- Transverse masses (mtw1, mtw2)
- Jet multiplicity
- b-jet multiplicity

## 🧠 Training
TheG BDT is trained using TMVA with:
- NTrees = 600
- MaxDepth = 3
- Gradient boosting
- Bagging enabled

## 📈 Results
- Optimal BDT cut: **0.66**
- Signal efficiency: **68%**
- Background efficiency: **4.9%**
- Clear signal/background separation

## Data Availability

The ROOT (`.root`) files used in this analysis are not included in the repository due to their large size and standard data management practices in High Energy Physics.

The repository contains:
- All analysis and plotting scripts
- TMVA configuration and trained BDT
- Final plots
- Full written report (PDF and LaTeX source)

Users can reproduce the analysis by running the provided scripts on locally available ROOT files with the same tree structure.

Detailed information about data access and required formats is available in [`DATA.md`](DATA.md).


## 📂 Repository Structure
WW-BDT-TMVA/
│── scripts/
│   ├── root_reduction.py
│   ├── variable_calculation.py
│   ├── train_tmva_bdt.py
│   ├── tmva_bdt.py
│   ├── plot_bdt_overlay.c
│   ├── plot_bdt_stack.c
│   └── plot_significance.c
│
│── plots/
│   ├── BDT_signal_vs_background.png
│   ├── BDT_stack.png
│   └── significance_vs_cut.png
│
│── report/
│   ├── WW_BDT_Report.pdf
│   └── WW_BDT_Report.tex
│
│── docs/
│   └── analysis_flow.png
│
│── DATA.md
│── README.md
│── .gitignore

## 🚀 How to Run

1. Train BDT:
python train_tmva_bdt.py

2. Apply BDT:
python tmva_bdt.py

3. Plot results using ROOT macros

📌 Notes
ROOT files are not included due to size.
Analysis intended for educational and research demonstration.

Author: Manan Makhija Tools: ROOT, TMVA, Python, uproot.