# import ROOT in batch mode
import math
import sys
import numpy as np
oldargv = sys.argv[:]
sys.argv = [ '-b-' ]
import ROOT
ROOT.gROOT.SetBatch(True)
sys.argv = oldargv

# load FWLite C++ libraries
ROOT.gSystem.Load("libFWCoreFWLite.so");
ROOT.gSystem.Load("libDataFormatsFWLite.so");
ROOT.AutoLibraryLoader.enable()

#Useful functions
dphi = ROOT.Math.VectorUtil.DeltaPhi
deltaR = ROOT.Math.VectorUtil.DeltaR

# load FWlite python libraries
from DataFormats.FWLite import Handle, Events

muons, muonLabel = Handle("std::vector<pat::Muon>"), "slimmedMuons"
electrons, electronLabel = Handle("std::vector<pat::Electron>"), "slimmedElectrons"
photons, photonLabel = Handle("std::vector<pat::Photon>"), "slimmedPhotons"
taus, tauLabel = Handle("std::vector<pat::Tau>"), "slimmedTaus"
jets, jetLabel = Handle("std::vector<pat::Jet>"), "slimmedJets"
fatjets, fatjetLabel = Handle("std::vector<pat::Jet>"), "slimmedJetsAK8"
mets, metLabel = Handle("std::vector<pat::MET>"), "slimmedMETs"
vertices, vertexLabel = Handle("std::vector<reco::Vertex>"), "offlineSlimmedPrimaryVertices"
verticesScore = Handle("edm::ValueMap<float>")
genparticles, genparticleLabel = Handle("std::vector<reco::GenParticle> "), "prunedGenParticles"


def Histo (events):

   xaxis = np.array([30., 50., 100., 200., 400., 800.])
   yaxis = np.array([-2.4, -1.6,-0.8,0.0,0.8,1.6,2.4])
   histo1 = ROOT.TH2F("bottom_eff", "B-tagging efficiency",5,xaxis, 6, yaxis)
   histo2 = ROOT.TH2F("charm_eff", "B-tagging efficiency",5,xaxis, 6, yaxis)
   histo3 = ROOT.TH2F("light_eff", "B-tagging efficiency",5,xaxis, 6, yaxis)
   histo_den1 = ROOT.TH2F("bottomEffDenominator", "B-tagging efficiency denominator", 5,xaxis, 6, yaxis)
   histo_den2 = ROOT.TH2F("charmEffDenominator", "B-tagging efficiency denominator", 5,xaxis, 6, yaxis)
   histo_den3 = ROOT.TH2F("lightEffDenominator", "B-tagging efficiency denominator", 5,xaxis, 6, yaxis)

   count1 = 0
   count2 = 0
   for iev,event in enumerate(events):#event loop
       if iev >= 5000000: break        #limit event loop
       event.getByLabel(muonLabel, muons)
       event.getByLabel(electronLabel, electrons)
       event.getByLabel(photonLabel, photons)
       event.getByLabel(tauLabel, taus)
       event.getByLabel(jetLabel, jets)
       event.getByLabel(fatjetLabel, fatjets)
       event.getByLabel(metLabel, mets)
       event.getByLabel(vertexLabel, vertices)
       event.getByLabel(vertexLabel, verticesScore)
       event.getByLabel(genparticleLabel, genparticles)
       if iev%10000 == 0: print "I am at event number:%5f"%iev 
       #print "\nEvent %d: run %6d, lumi %4d, event %12d" % (iev,event.eventAuxiliary().run(), event.eventAuxiliary().luminosityBlock(),event.eventAuxiliary().event())                  # Vertices
       if len(vertices.product()) == 0 or vertices.product()[0].ndof() < 4:
       #    print "Event has no good primary vertex."
           continue
       else:
           PV = vertices.product()[0]
       #    print "PV at x,y,z = %+5.3f, %+5.3f, %+6.3f, ndof: %.1f, score: (pt2 of clustered objects) %.1f" % (PV.x(), PV.y(), PV.z(), PV.ndof(),verticesScore.product().get(0))

       #for x,gen in enumerate(genparticles.product()):
	#	print gen.pdgId()  

       
       # Jets (standard AK4)    
       for i,j in enumerate(jets.product()):
           if j.pt() < 30: continue
           if abs(j.eta()) > 2.4: continue
           if j.neutralHadronEnergyFraction() > 0.90: continue
           if j.neutralEmEnergyFraction() > 0.90: continue
           if j.chargedHadronEnergyFraction() == 0: continue
           if j.muonEnergyFraction() > 0.8: continue
           if j.chargedEmEnergyFraction() > 0.90: continue
           if (j.chargedMultiplicity()+j.neutralMultiplicity()) < 2: continue
           if j.chargedMultiplicity() < 1: continue
           if j.partonFlavour() == 5:
                histo_den1.Fill(j.pt(),j.eta(),1.0)	   
           	if j.bDiscriminator("pfDeepCSVJetTags:probb") > 0.4941:
			histo1.Fill(j.pt(),j.eta(),1.0)
           if j.partonFlavour() == 4:
                histo_den2.Fill(j.pt(),j.eta(),1.0)
                if j.bDiscriminator("pfDeepCSVJetTags:probb") > 0.4941:
                        histo2.Fill(j.pt(),j.eta(),1.0)
           if j.partonFlavour() == 0:
                histo_den3.Fill(j.pt(),j.eta(),1.0)
                if j.bDiscriminator("pfDeepCSVJetTags:probb") > 0.4941:
                        histo3.Fill(j.pt(),j.eta(),1.0)
   histo1.Divide(histo_den1)
   histo2.Divide(histo_den2)
   histo3.Divide(histo_den3)
   histo1.SetLineWidth(3)
   histo1.GetXaxis().SetTitle("Jet p_{T}")
   histo1.GetYaxis().SetTitle("Jet #eta")
   histo1.Draw("COLZ")
   histo2.SetLineWidth(3)
   histo2.GetXaxis().SetTitle("Jet p_{T}")
   histo2.GetYaxis().SetTitle("Jet #eta")
   histo2.Draw("COLZ")
   histo3.SetLineWidth(3)
   histo3.GetXaxis().SetTitle("Jet p_{T}")
   histo3.GetYaxis().SetTitle("Jet #eta")
   histo3.Draw("COLZ")
   histo1.SaveAs("2016_eff1.root")
   histo2.SaveAs("2016_eff2.root")
   histo3.SaveAs("2016_eff3.root")
   return 


#DY Inclusive
#events = Events('root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext2-v1/100000/00099D43-77ED-E611-8889-5065F381E1A1.root')
#2016 TTTo2L2Nu
events = Events([      
                        'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv3/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/100000/00960D0A-6F75-E911-8B07-002590D9D9FC.root',
                        'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv3/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/10000/F8203C59-B777-E911-AB2B-0025905C975E.root',
                        'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv3/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/10000/F6A12E34-6E79-E911-BE4A-98039B3B01CA.root',
                        'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv3/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/10000/F62D9F55-C171-E911-84B3-3CFDFE6349A0.root',
                        'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv3/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/10000/EE683B95-CE78-E911-9D63-90E2BAD1BDF0.root',
                        'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv3/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/10000/E6FDB69C-9E7A-E911-AA63-AC1F6B0DE4AC.root',
                        'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv3/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/10000/E41760C0-FB79-E911-A16B-FA163E0EED24.root',
                        'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv3/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/10000/DEA9AD1F-6E79-E911-B31D-20040FE94280.root',
                        'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv3/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/10000/DCD4B6CC-7079-E911-946E-008CFA197D98.root',
                        'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv3/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/10000/DAB35062-6E79-E911-81A0-0CC47AD98D6C.root',
                        'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv3/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/10000/D0AACF9B-1573-E911-9EE8-001E6779257C.root',
                        'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv3/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/10000/CAFB7C79-4E73-E911-AC29-0242AC1C0500.root',
                        'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv3/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/10000/C23518D0-6F79-E911-BAB5-0CC47AF9B302.root',
                        'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv3/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/10000/C0674A04-D771-E911-B09E-F01FAFDA8A5A.root',
                        'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv3/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/10000/BEAFAD14-7079-E911-90D1-7CD30AC030F8.root',
                        'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv3/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/10000/B6714B75-B477-E911-9E0D-0CC47AF9B2CE.root',
                        'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv3/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/10000/B22C31DB-3B84-E911-88BE-008CFAF750B6.root',
                        'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv3/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/10000/A0784C2A-7079-E911-BB84-D4AE526A091F.root',
                        'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv3/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/10000/983B5F57-C87B-E911-8BC5-00259075D72C.root',
                        'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv3/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/10000/983B5F57-C87B-E911-8BC5-00259075D72C.root',
                        'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv3/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/10000/96DDE57B-F779-E911-BD34-0CC47AFC3C18.root',
                        'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv3/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/10000/8C180B7C-B871-E911-8A06-FA163E489C59.root',
                        'root://cms-xrd-global.cern.ch//store/mc/RunIISummer16MiniAODv3/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v1/10000/7491745C-6F79-E911-BF78-0242AC1C0503.root'
])
histogram = Histo(events)