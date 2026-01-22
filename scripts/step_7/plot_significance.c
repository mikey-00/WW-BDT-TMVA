void plot_significance() {

    TFile *f_sig = TFile::Open("step_4/ww_signal_withBDT.root");
    TFile *f_tt  = TFile::Open("step_4/ttbar_background_withBDT.root");
    TFile *f_tw  = TFile::Open("step_4/tw_top_background_withBDT.root");
    TFile *f_twa = TFile::Open("step_4/tw_antitop_background_withBDT.root");

    TTree *ts = (TTree*)f_sig->Get("Events");
    TTree *tt = (TTree*)f_tt->Get("Events");
    TTree *tw = (TTree*)f_tw->Get("Events");
    TTree *twa= (TTree*)f_twa->Get("Events");

    const int nCuts = 50;
    TH1F *hZ = new TH1F("hZ","Significance vs BDT cut;BDT cut;S/#sqrt{S+B}",
                        nCuts,-1,1);

    for (int i = 1; i <= nCuts; i++) {
        double cut = hZ->GetBinCenter(i);

        double S = ts->GetEntries(Form("BDT_score > %f",cut));
        double B = tt->GetEntries(Form("BDT_score > %f",cut))
                 + tw->GetEntries(Form("BDT_score > %f",cut))
                 + twa->GetEntries(Form("BDT_score > %f",cut));

        if (S+B > 0)
            hZ->SetBinContent(i, S / sqrt(S+B));
    }

    int bestBin = hZ->GetMaximumBin();
    double bestCut = hZ->GetBinCenter(bestBin);
    double bestZ   = hZ->GetBinContent(bestBin);

    cout << "Optimal BDT cut = " << bestCut << endl;
    cout << "Max significance = " << bestZ << endl;

    TCanvas *c = new TCanvas("c","Significance",800,600);
    hZ->Draw("HIST");

    TLine *line = new TLine(bestCut,0,bestCut,bestZ);
    line->SetLineStyle(2);
    line->Draw();

    c->SaveAs("plots/significance_vs_cut.png");
}
