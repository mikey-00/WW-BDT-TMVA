# Data Description and Availability

## Overview

This project performs a multivariate analysis using Boosted Decision Trees (BDTs)
to separate WW signal events from dominant top-quark backgrounds using the
ROOT TMVA framework.

The analysis relies on Monte Carlo simulated datasets stored in ROOT (`.root`)
format and structured as TTrees.

## Data Availability

The ROOT input files used in this analysis are **not included** in this repository.

This is due to:
- Large file sizes
- Standard data handling practices in High Energy Physics
- Dataset ownership and storage constraints

Only analysis code, configuration files, plots, and documentation are provided.

## Datasets Used

The analysis uses the following Monte Carlo samples:

- **Signal**
  - WW (diboson production)

- **Backgrounds**
  - ttbar ($t\bar{t}$)
  - single top tW
  - single anti-top $\bar{t}W$

Each dataset is processed independently and later combined at the analysis level
for training and evaluation.

## Data Format Requirements

To reproduce the analysis, the ROOT files must satisfy the following conditions:

- Contain a TTree named consistently across samples
- Include the following branches (or equivalent):

  - Lepton kinematics:  
    `pt1`, `pt2`, `eta1`, `eta2`
  - Dilepton variables:  
    `mll`, `ptll`, `dphill`
  - Missing transverse energy:  
    `PuppiMET_pt`
  - Transverse masses:  
    `mtw1`, `mtw2`
  - Jet information:  
    `nJet`, `nBJet`

- Signal and background samples must use identical variable definitions and units

## Preprocessing

Before training:
- Variables are checked for consistency and physical ranges
- No event weights or cross-section normalization are applied
- The analysis focuses on **relative efficiencies**, not absolute yields

## Reproducibility

Users can reproduce the analysis by:
1. Providing ROOT files with the required tree structure and variables
2. Running the training script:
   ```bash
   python train_tmva_bdt.py
Applying the trained BDT:

python tmva_bdt.py
Generating plots using the provided ROOT macros

Notes
This dataset description is sufficient for academic evaluation and reproducibility

The analysis is intended for educational and research demonstration purposes

No proprietary or restricted data is distributed with this repository