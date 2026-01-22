import ROOT
import time

# =============================================================================
# Helper utilities
# =============================================================================
def banner(msg):
    print("\n" + "="*80)
    print(f"▶ {msg}")
    print("="*80)

def timed(msg, start):
    print(f"⏱ {msg} took {time.time() - start:.1f} s")

def open_root(path):
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise FileNotFoundError(f"❌ Cannot open ROOT file: {path}")
    print(f"✅ Loaded: {path}")
    return f

# =============================================================================
# 0. START
# =============================================================================
t0 = time.time()
banner("Starting TMVA BDT Training (WW vs Top backgrounds)")

# =============================================================================
# 1. INITIALIZE TMVA
# =============================================================================
t = time.time()
ROOT.TMVA.Tools.Instance()
ROOT.TMVA.PyMethodBase.PyInitialize()
timed("TMVA initialization", t)

# =============================================================================
# 2. OUTPUT FILE
# =============================================================================
output = ROOT.TFile("TMVA.root", "RECREATE")

factory = ROOT.TMVA.Factory(
    "TMVAClassification",
    output,
    "V:Color:DrawProgressBar:AnalysisType=Classification"
)

loader = ROOT.TMVA.DataLoader("dataset")

# =============================================================================
# 3. INPUT VARIABLES (optimized)
# =============================================================================
banner("Adding input variables")

variables = [
    "pt1", "pt2",
    "Lepton_eta0", "Lepton_eta1",
    "mll", "ptll", "dphill",
    "PuppiMET_pt",
    "mtw1", "mtw2",
    "nJet", "nBJet"
]

for v in variables:
    loader.AddVariable(v, "F")
    print(f"  + {v}")

print(f"Total variables: {len(variables)}")

# =============================================================================
# 4. LOAD ROOT FILES
# =============================================================================
banner("Loading ROOT files")

f_sig = open_root("/mnt/e/project/small_root/step_3/ww_signal.root")
f_tt  = open_root("/mnt/e/project/small_root/step_3/ttbar_background.root")
f_tw  = open_root("/mnt/e/project/small_root/step_3/tw_top_background.root")
f_twa = open_root("/mnt/e/project/small_root/step_3/tw_anti_top_background.root")

t_sig = f_sig.Get("Events")
t_tt  = f_tt.Get("Events")
t_tw  = f_tw.Get("Events")
t_twa = f_twa.Get("Events")

print("\n📊 Event counts:")
print(f"  Signal WW:        {t_sig.GetEntries():,}")
print(f"  tt̄ background:   {t_tt.GetEntries():,}")
print(f"  tW (top):         {t_tw.GetEntries():,}")
print(f"  tW (antitop):     {t_twa.GetEntries():,}")

# =============================================================================
# 5. REGISTER TREES
# =============================================================================
banner("Registering signal and background trees")

loader.AddSignalTree(t_sig, 1.0)

loader.AddBackgroundTree(t_tt,  1.0)
loader.AddBackgroundTree(t_tw,  1.0)
loader.AddBackgroundTree(t_twa, 1.0)

# =============================================================================
# 6. TRAIN / TEST SPLIT
# =============================================================================
banner("Preparing training and test samples")

loader.PrepareTrainingAndTestTree(
    ROOT.TCut(""),
    "nTrain_Signal=0:"
    "nTrain_Background=0:"
    "SplitMode=Random:"
    "NormMode=NumEvents:"
    "V"
)

# =============================================================================
# 7. BOOK BDT
# =============================================================================
banner("Booking BDT")

factory.BookMethod(
    loader,
    ROOT.TMVA.Types.kBDT,
    "BDT",
    "V:"
    "NTrees=600:"
    "MaxDepth=3:"
    "BoostType=Grad:"
    "Shrinkage=0.08:"
    "UseBaggedBoost:"
    "BaggedSampleFraction=0.6:"
    "SeparationType=GiniIndex:"
    "nCuts=30"
)

# =============================================================================
# 8. TRAIN / TEST / EVALUATE
# =============================================================================
banner("Training BDT ⏳ (this may take a few minutes)")
t_train = time.time()
factory.TrainAllMethods()
timed("Training", t_train)

banner("Testing BDT")
t_test = time.time()
factory.TestAllMethods()
timed("Testing", t_test)

banner("Evaluating BDT")
t_eval = time.time()
factory.EvaluateAllMethods()
timed("Evaluation", t_eval)

# =============================================================================
# 9. FINISH
# =============================================================================
output.Close()

banner("TMVA BDT training completed successfully 🎉")
timed("Total runtime", t0)
print("📁 Output saved as TMVA.root")
