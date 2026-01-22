import uproot
import awkward as ak
import numpy as np
import glob
from tqdm import tqdm

# ============================
# CONFIGURATION
# ============================
input_files = glob.glob(r"/mnt/e/project/small_root/step_2/background/ttbar/*.root")
tree_name = "Events"
output_file = "ttbar_background.root"
chunk_size = 100_000  # adjust as needed

# ============================
# HELPER FUNCTIONS
# ============================
def delta_phi(phi1, phi2):
    dphi = np.abs(phi1 - phi2)
    return np.where(dphi > np.pi, 2*np.pi - dphi, dphi)

def delta_r(eta1, phi1, eta2, phi2):
    return np.sqrt((eta1 - eta2)**2 + delta_phi(phi1, phi2)**2)

def invariant_mass(pt1, eta1, phi1, pt2, eta2, phi2, mass1=0, mass2=0):
    e1 = np.sqrt((pt1*np.cosh(eta1))**2 + mass1**2)
    e2 = np.sqrt((pt2*np.cosh(eta2))**2 + mass2**2)
    px1, py1, pz1 = pt1*np.cos(phi1), pt1*np.sin(phi1), pt1*np.sinh(eta1)
    px2, py2, pz2 = pt2*np.cos(phi2), pt2*np.sin(phi2), pt2*np.sinh(eta2)
    m2 = (e1+e2)**2 - ((px1+px2)**2 + (py1+py2)**2 + (pz1+pz2)**2)
    return np.sqrt(np.maximum(m2, 0))

def transverse_mass(pt, met_pt, dphi):
    return np.sqrt(2 * pt * met_pt * (1 - np.cos(dphi)))

# ============================
# OUTPUT ROOT INIT
# ============================
print(f"📁 Creating output: {output_file}")
fout = uproot.recreate(output_file)
tree_created = False

# ============================
# PROCESS PER FILE + PER CHUNK
# ============================
branches = [
    "Electron_charge","Muon_charge",
    "Electron_pt","Electron_eta","Electron_phi",
    "Muon_pt","Muon_eta","Muon_phi","Muon_mass",
    "Jet_pt","Jet_eta","Jet_phi","Jet_mass","Jet_btagDeepFlavB",
    "PuppiMET_pt","PuppiMET_phi"
]

total_written = 0

for f in input_files:
    with uproot.open(f) as file:
        tree = file[tree_name]
        n = tree.num_entries
        print(f"\n📌 File: {f} | Entries: {n:,}")

        for start in tqdm(range(0, n, chunk_size), desc="⏳ Chunks"):
            stop = min(start + chunk_size, n)
            data = tree.arrays(branches, entry_start=start, entry_stop=stop, library="ak")
            # Exactly 1 electron and 1 muon
            mask_emu = (ak.num(data.Electron_pt) == 1) & (ak.num(data.Muon_pt) == 1)
            data = data[mask_emu]

            # Opposite-sign requirement
            os_mask = (data.Electron_charge[:,0] * data.Muon_charge[:,0]) < 0
            data = data[os_mask]

            if len(data) == 0:
                continue


            # ============ LEPTONS ============
            lep_pt  = ak.concatenate([data.Electron_pt,  data.Muon_pt], axis=1)
            lep_eta = ak.concatenate([data.Electron_eta, data.Muon_eta], axis=1)
            lep_phi = ak.concatenate([data.Electron_phi, data.Muon_phi], axis=1)
            lep_mass = ak.concatenate([ak.zeros_like(data.Electron_pt), data.Muon_mass], axis=1)

            order = ak.argsort(lep_pt, ascending=False)
            lep_pt, lep_eta, lep_phi, lep_mass = lep_pt[order], lep_eta[order], lep_phi[order], lep_mass[order]

            pt1, pt2 = ak.fill_none(lep_pt[:,0],0), ak.fill_none(lep_pt[:,1],0)
            eta1, eta2 = ak.fill_none(lep_eta[:,0],0), ak.fill_none(lep_eta[:,1],0)
            phi1, phi2 = ak.fill_none(lep_phi[:,0],0), ak.fill_none(lep_phi[:,1],0)

            met_pt  = ak.to_numpy(data.PuppiMET_pt)
            met_phi = ak.to_numpy(data.PuppiMET_phi)

            # Lepton Vars
            mll   = invariant_mass(pt1,eta1,phi1,pt2,eta2,phi2)
            drll  = delta_r(eta1,phi1,eta2,phi2)
            dphill = delta_phi(phi1,phi2)

            dphillmet1 = delta_phi(phi1, met_phi)
            dphillmet2 = delta_phi(phi2, met_phi)

            px1, py1 = pt1*np.cos(phi1), pt1*np.sin(phi1)
            px2, py2 = pt2*np.cos(phi2), pt2*np.sin(phi2)
            phi_ll = np.arctan2(py1+py2, px1+px2)
            dphillmet = delta_phi(phi_ll, met_phi)

            ptll = np.sqrt((px1+px2)**2 + (py1+py2)**2)

            mtw1 = transverse_mass(pt1, met_pt, dphillmet1)
            mtw2 = transverse_mass(pt2, met_pt, dphillmet2)

            pxmiss, pymiss = met_pt*np.cos(met_phi), met_pt*np.sin(met_phi)
            pTWW = np.sqrt((px1+px2+pxmiss)**2 + (py1+py2+pymiss)**2)

            # ============ JETS ============
            jets_pt  = data.Jet_pt
            jets_eta = data.Jet_eta
            jets_phi = data.Jet_phi
            btag = data.Jet_btagDeepFlavB

            # Jet selection (CMS-like)
            jet_mask = (jets_pt > 30) & (abs(jets_eta) < 2.4)

            jets_pt  = jets_pt[jet_mask]
            jets_eta = jets_eta[jet_mask]
            jets_phi = jets_phi[jet_mask]
            btag     = btag[jet_mask]

            # Jet multiplicities
            nJet = ak.num(jets_pt)

            # b-jet counting (DeepFlavB medium WP)
            btag_wp = 0.277
            nBJet = ak.sum(btag > btag_wp, axis=1)

            order_j = ak.argsort(jets_pt, ascending=False)
            jets_pt, jets_eta, jets_phi, btag = (
                jets_pt[order_j], jets_eta[order_j], jets_phi[order_j], btag[order_j]
            )

            jets_pt_p  = ak.pad_none(jets_pt, 2)
            jets_eta_p = ak.pad_none(jets_eta, 2)
            jets_phi_p = ak.pad_none(jets_phi, 2)
            btag_p     = ak.pad_none(btag, 2)

            j1_pt  = ak.fill_none(jets_pt_p[:,0], 0)
            j2_pt  = ak.fill_none(jets_pt_p[:,1], 0)
            j1_eta = ak.fill_none(jets_eta_p[:,0], 0)
            j2_eta = ak.fill_none(jets_eta_p[:,1], 0)
            j1_phi = ak.fill_none(jets_phi_p[:,0], 0)
            j2_phi = ak.fill_none(jets_phi_p[:,1], 0)
            j1_btag = ak.fill_none(btag_p[:,0], -2)
            j2_btag = ak.fill_none(btag_p[:,1], -2)

            mjj = invariant_mass(j1_pt, j1_eta, j1_phi, j2_pt, j2_eta, j2_phi)
            detajj = np.abs(j1_eta - j2_eta)
            dphijj = delta_phi(j1_phi, j2_phi)

            pxjj = j1_pt*np.cos(j1_phi) + j2_pt*np.cos(j2_phi)
            pyjj = j1_pt*np.sin(j1_phi) + j2_pt*np.sin(j2_phi)
            phi_jj = np.arctan2(pyjj, pxjj)
            dphijjmet = delta_phi(phi_jj, met_phi)

            detajj_matrix = np.abs(jets_eta[:, :, None] - jets_eta[:, None, :])
            mindetajj = ak.fill_none(ak.min(ak.min(detajj_matrix, axis=2), axis=1), 0)

            px_hjj = (px1 + px2 + pxmiss) + (j1_pt*np.cos(j1_phi) + j2_pt*np.cos(j2_phi))
            py_hjj = (py1 + py2 + pymiss) + (j1_pt*np.sin(j1_phi) + j2_pt*np.sin(j2_phi))
            pTHjj = np.sqrt(px_hjj**2 + py_hjj**2)

            # ============ SAVE CHUNK ============
            out_dict = {
            "pt1": pt1, "pt2": pt2,
            "Lepton_eta0": eta1, "Lepton_eta1": eta2,
            "mll": mll, "drll": drll, "dphill": dphill,
            "dphillmet": dphillmet, "dphillmet1": dphillmet1, "dphillmet2": dphillmet2,
            "ptll": ptll, "mtw1": mtw1, "mtw2": mtw2,
            "PuppiMET_pt": met_pt, "pTWW": pTWW,
            "pTHjj": pTHjj, "mjj": mjj, "detajj": detajj, "dphijj": dphijj,
            "dphijjmet": dphijjmet, "mindetajj": mindetajj,
            "CleanJet_pt0": j1_pt, "CleanJet_pt1": j2_pt,
            "CleanJet_eta0": j1_eta, "CleanJet_eta1": j2_eta,
            "Jet_btagDeepFlavB_jetIdx0": j1_btag,
            "Jet_btagDeepFlavB_jetIdx1": j2_btag,
            "nJet": nJet,
            "nBJet": nBJet,
            }

            n_events = len(pt1)

            if n_events == 0:
                continue   # 🚑 skip empty chunks safely

            if not tree_created:
                fout["Events"] = out_dict      # ✅ create tree
                tree_created = True
            else:
                fout["Events"].extend(out_dict)  # ✅ append

            total_written += len(pt1)
            del data  # free RAM

print(f"\n🎉 Finished! Total written events: {total_written:,}")
