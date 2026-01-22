import ROOT
import array
import uproot
import awkward as ak
import numpy as np

# =============================================================================
# CONFIG
# =============================================================================
TMVA_FILE = "TMVA.root"
METHOD_NAME = "BDT"
TREE_NAME = "Events"

input_file  = r"/mnt/e/project/small_root/step_3/ttbar_background.root"
output_file = r"/mnt/e/project/small_root/step_4/ttbar_background_withBDT.root"

# =============================================================================
# 1. SETUP TMVA READER
# =============================================================================
ROOT.TMVA.Tools.Instance()
reader = ROOT.TMVA.Reader("!Color:!Silent")

# Variables (ORDER MATTERS)
var_names = [
    "pt1", "pt2",
    "Lepton_eta0", "Lepton_eta1",
    "mll", "ptll", "dphill",
    "PuppiMET_pt",
    "mtw1", "mtw2",
    "nJet", "nBJet"
]

var_arrays = {}
for v in var_names:
    var_arrays[v] = array.array('f', [0.])
    reader.AddVariable(v, var_arrays[v])

# Load trained BDT
reader.BookMVA(
    METHOD_NAME,
    "dataset/weights/TMVAClassification_BDT.weights.xml"
)

print("✅ TMVA Reader initialized")

# =============================================================================
# 2. LOAD INPUT TREE (uproot)
# =============================================================================
file = uproot.open(input_file)
tree = file[TREE_NAME]
data = tree.arrays(var_names, library="ak")

n_events = len(data)
print(f"📊 Events to process: {n_events:,}")

# =============================================================================
# 3. APPLY BDT
# =============================================================================
bdt_scores = np.zeros(n_events, dtype=np.float32)

print("🚀 Evaluating BDT...")
for i in range(n_events):
    for v in var_names:
        var_arrays[v][0] = float(data[v][i])
    bdt_scores[i] = reader.EvaluateMVA(METHOD_NAME)

print("✅ BDT evaluation done")

# =============================================================================
# 4. WRITE NEW ROOT FILE
# =============================================================================
out_dict = {v: data[v] for v in var_names}
out_dict["BDT_score"] = bdt_scores

with uproot.recreate(output_file) as fout:
    fout[TREE_NAME] = out_dict

print(f"🎉 Output written to: {output_file}")
