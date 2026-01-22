void plot_bdt_stack() {
    TFile *f_sig = TFile::Open("step_4/ww_signal_withBDT.root");
    TFile *f_tt  = TFile::Open("step_4/ttbar_background_withBDT.root");
    TFile *f_tw  = TFile::Open("step_4/tw_top_background_withBDT.root");
    TFile *f_twa = TFile::Open("step_4/tw_antitop_background_withBDT.root");

    TTree *ts = (TTree*)f_sig->Get("Events");
    TTree *tt = (TTree*)f_tt->Get("Events");
    TTree *tw = (TTree*)f_tw->Get("Events");
    TTree *twa= (TTree*)f_twa->Get("Events");

    const int nCuts = 50;
    double cutMin = -1.0;
    double cutMax = 1.0;
    double step   = (cutMax - cutMin)/nCuts;

    TH1F *hZ = new TH1F("hZ","BDT Cut Optimization;BDT cut;S/#sqrt{S+B}",nCuts,cutMin,cutMax);

    for (int i = 1; i <= nCuts; i++) {
        double cut = hZ->GetBinCenter(i);

        double S = ts->GetEntries(Form("BDT_score > %f",cut));

        double B = 0;
        B += tt->GetEntries(Form("BDT_score > %f",cut));
        B += tw->GetEntries(Form("BDT_score > %f",cut));
        B += twa->GetEntries(Form("BDT_score > %f",cut));

        if (S + B > 0) {
            double Z = S / sqrt(S + B);
            hZ->SetBinContent(i, Z);
        }
    }

    int bestBin = hZ->GetMaximumBin();
    double bestCut = hZ->GetBinCenter(bestBin);
    double bestZ   = hZ->GetBinContent(bestBin);

    cout << "✅ Optimal BDT cut = " << bestCut << endl;
    cout << "⭐ Max Significance = " << bestZ << endl;

    TCanvas *c = new TCanvas("c","BDT Cut Optimization",800,600);
    hZ->SetLineWidth(2);
    hZ->Draw("HIST");

    TLine *line = new TLine(bestCut,0,bestCut,bestZ);
    line->SetLineStyle(2);
    line->SetLineWidth(2);
    line->Draw();

    double S_total = ts->GetEntries();
    double B_total = tt->GetEntries() + tw->GetEntries() + twa->GetEntries();

    double S_eff = ts->GetEntries(Form("BDT_score > %f",bestCut)) / S_total;
    double B_eff = (tt->GetEntries(Form("BDT_score > %f",bestCut))
                   +tw->GetEntries(Form("BDT_score > %f",bestCut))
                   +twa->GetEntries(Form("BDT_score > %f",bestCut))) / B_total;

    cout << "Signal efficiency = " << S_eff << endl;
    cout << "Background efficiency = " << B_eff << endl;

    c->SaveAs("plots/BDT_stack.png");
}