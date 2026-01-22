void plot_bdt_overlay() {
    TFile *f_sig = TFile::Open("step_4/ww_signal_withBDT.root");
    TFile *f_tt  = TFile::Open("step_4/ttbar_background_withBDT.root");
    TFile *f_tw  = TFile::Open("step_4/tw_top_background_withBDT.root");
    TFile *f_twa = TFile::Open("step_4/tw_antitop_background_withBDT.root");

    TTree *ts = (TTree*)f_sig->Get("Events");
    TTree *tt = (TTree*)f_tt->Get("Events");
    TTree *tw = (TTree*)f_tw->Get("Events");
    TTree *twa= (TTree*)f_twa->Get("Events");

    TH1F *h_sig = new TH1F("h_sig","BDT Score;BDT score;Events",40,-1,1);
    TH1F *h_bkg = new TH1F("h_bkg","",40,-1,1);

    ts->Draw("BDT_score>>h_sig");
    tt->Draw("BDT_score>>+h_bkg");
    tw->Draw("BDT_score>>+h_bkg");
    twa->Draw("BDT_score>>+h_bkg");

    h_sig->SetLineColor(kRed);
    h_sig->SetLineWidth(2);
    h_bkg->SetLineColor(kBlue);
    h_bkg->SetLineWidth(2);

    h_sig->Draw("HIST");
    h_bkg->Draw("HIST SAME");

    auto leg = new TLegend(0.65,0.75,0.88,0.88);
    leg->AddEntry(h_sig,"WW Signal","l");
    leg->AddEntry(h_bkg,"Top Background","l");
    leg->Draw();

    h_sig->Scale(1.0 / h_sig->Integral());
    h_bkg->Scale(1.0 / h_bkg->Integral());

    h_sig->SetTitle("Normalized BDT Score;BDT score;A.U.");
    h_sig->Draw("HIST");
    h_bkg->Draw("HIST SAME");

    TH1F *h_tt  = new TH1F("h_tt","",40,-1,1);
    TH1F *h_tw  = new TH1F("h_tw","",40,-1,1);
    TH1F *h_twa = new TH1F("h_twa","",40,-1,1);

    tt->Draw("BDT_score>>h_tt");
    tw->Draw("BDT_score>>h_tw");
    twa->Draw("BDT_score>>h_twa");

    h_tt->SetFillColor(kBlue-7);
    h_tw->SetFillColor(kGreen-6);
    h_twa->SetFillColor(kAzure-9);

    THStack *hs = new THStack("hs","BDT Score;BDT score;Events");
    hs->Add(h_tt);
    hs->Add(h_tw);
    hs->Add(h_twa);

    hs->Draw("HIST");
    h_sig->Draw("HIST SAME");

    auto leg2 = new TLegend(0.6,0.6,0.88,0.88);
    leg2->AddEntry(h_sig,"WW Signal","l");
    leg2->AddEntry(h_tt,"ttbar","f");
    leg2->AddEntry(h_tw,"tW","f");
    leg2->AddEntry(h_twa,"#bar{t}W","f");
    leg2->Draw();

    double cut = 0.4;
    TLine *line = new TLine(cut,0,cut,h_sig->GetMaximum());
    line->SetLineStyle(2);
    line->SetLineWidth(2);
    line->Draw();

    TCanvas *c = new TCanvas("c","BDT",800,600);
    h_sig->Draw("HIST");
    h_bkg->Draw("HIST SAME");
    c->SaveAs("plots/BDT_signal_vs_background.png");
}