import uproot
import awkward as ak
import numpy as np
import glob

#SAVE FUNCTION
"""Saves all branches (including jagged ones) safely into a new ROOT file.
   Only skips truly invalid arrays (None or empty)."""
def save_reduced_file(output_filename, selected_events):
    import numpy as np
    import awkward as ak
    import uproot

    with uproot.recreate(output_filename) as fout:
        tree_dict = {}
        total = len(selected_events.fields)
        kept = 0

        for branch in selected_events.fields:
            arr = selected_events[branch]
            try:
                #Handle Awkward Arrays and numpy arrays differently
                if isinstance(arr, ak.Array):
                    #Skip completely empty arrays
                    if len(arr) == 0:
                        print(f"Skipping {branch}: empty array")
                        continue
                    tree_dict[branch] = arr
                else:
                    np_arr = np.asarray(arr)
                    if np_arr.size == 0:
                        print(f"Skipping {branch}: empty np array")
                        continue
                    tree_dict[branch] = np_arr

                kept += 1

            except Exception as e:
                print(f"Skipping branch {branch} due to write error: {e}")

        if not tree_dict:
            raise ValueError("No valid branches to write! Tree would be empty.")

        fout["Events"] = tree_dict
        print(f"Successfully wrote {kept}/{total} branches and {len(selected_events)} events to '{output_filename}'")

#MAIN EXECUTION
if __name__ == "__main__":
    #Locate input ROOT files
    input_files = glob.glob(r"/mnt/e/project/small_root/ttbar/ttbar_10/*.root")
    print("🔍 Found files:", input_files)

    if not input_files:
        raise FileNotFoundError("❌ No ROOT files found in the given directory.")

    output_file = "ttbar_10_reduced.root" #input("Enter the name of the reduced .root file (e.g. reduced.root): ")

    #Branch list (variables to extract)
    branches = [
        "nMuon", "nElectron",
    "Electron_pt","Electron_eta","Electron_phi",
    "Muon_pt","Muon_eta","Muon_phi","Muon_mass",
    "Jet_pt","Jet_eta","Jet_phi","Jet_mass","Jet_btagDeepFlavB",
    "PuppiMET_pt","PuppiMET_phi",
    "Electron_charge",
    "Muon_charge",
    ]

    #Load and merge all data
    all_data = []
    for i, fname in enumerate(input_files, 1):
        print(f"\n📂 Processing file {i}: {fname}")
        try:
            with uproot.open(fname) as file:
                tree = file["Events"]
                available = [b for b in branches if b in tree.keys()]
                missing = [b for b in branches if b not in tree.keys()]
                if missing:
                    print(f"⚠️ Missing branches: {missing}")
                arrays = tree.arrays(available)
                all_data.append(arrays)
        except Exception as e:
            print(f"❌ Skipping {fname} due to error: {e}")

    if not all_data:
        raise ValueError("❌ No valid ROOT files processed successfully.")

    #Merge all events
    data = ak.concatenate(all_data, axis=0)
    print(f"\n✅ Total events after merge: {len(data)}")

    #Apply basic event selection
    selected_events = data[(data["nMuon"] >= 1) & (data["nElectron"] >= 1)]
    print(f"✅ Events after selection: {len(selected_events)}")

    #Save reduced ROOT file (handles jagged arrays)
    save_reduced_file(output_file, selected_events)

    print("🎯 All done!")