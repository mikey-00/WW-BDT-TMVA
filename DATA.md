# Data Availability

This repository follows standard High Energy Physics (HEP) best practices regarding data management.

## ROOT Files

The input datasets used in this analysis are stored in ROOT (`.root`) format and include:

- `ww_signal.root`
- `ttbar_background.root`
- `tw_top_background.root`
- `tw_antitop_background.root`
- Corresponding files with BDT scores (step_4)

These ROOT files are **not included in the GitHub repository** due to:
- Large file sizes
- Storage and bandwidth limitations of GitHub
- Common practice in experimental physics collaborations

## How to Obtain the Data

The ROOT files can be:
- Generated locally by following the preprocessing and TMVA training scripts
- Provided upon reasonable academic request
- Replaced with equivalent datasets having the same tree structure and branch names

## Required Tree Structure

All ROOT files must contain a TTree named:

Events


with the following branches (used for BDT evaluation):

- pt1, pt2
- Lepton_eta0, Lepton_eta1
- mll, ptll, dphill
- PuppiMET_pt
- mtw1, mtw2
- nJet, nBJet
- BDT_score (for post-TMVA analysis)

## Reproducibility

All analysis steps, plotting macros, and significance calculations are fully reproducible using:
- The provided ROOT macros in `scripts/`
- The trained TMVA weights
- User-supplied ROOT files with the same structure

Final plots and numerical results are included in the repository.