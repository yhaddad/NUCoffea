"""
WSProducer.py
Workspace producers using coffea.
"""
from coffea.hist import Hist, Bin, export1d
from coffea.processor import ProcessorABC, LazyDataFrame, dict_accumulator
from uproot import recreate


class WSProducer(ProcessorABC):
    """
    A coffea Processor which produces a workspace.
    This applies selections and produces histograms from kinematics.
    """

    histograms = NotImplemented
    selection = NotImplemented

    def __init__(self, isMC, era=2017, sample="DY", do_syst=False, syst_var='', weight_syst=False, haddFileName=None, flag=False):
        self._flag = flag
        self.do_syst = do_syst
        self.era = era
        self.isMC = isMC
        self.sample = sample
        self.syst_var, self.syst_suffix = (syst_var, f'_sys_{syst_var}') if do_syst and syst_var else ('', '')
        self.weight_syst = weight_syst
        self._accumulator = dict_accumulator({
            name: Hist('Events', Bin(name=name, **axis))
            for name, axis in ((self.naming_schema(hist['name'], region), hist['axis'])
                               for _, hist in list(self.histograms.items())
                               for region in hist['region'])
        })
        self.outfile = haddFileName

    def __repr__(self):
        return f'{self.__class__.__name__}(era: {self.era}, isMC: {self.isMC}, sample: {self.sample}, do_syst: {self.do_syst}, syst_var: {self.syst_var}, weight_syst: {self.weight_syst}, output: {self.outfile})'

    @property
    def accumulator(self):
        return self._accumulator

    def process(self, df, *args):
        output = self.accumulator.identity()

        weight = self.weighting(df)

        for h, hist in list(self.histograms.items()):
            for region in hist['region']:
                name = self.naming_schema(hist['name'], region)
                selec = self.passbut(df, hist['target'], region)
                output[name].fill(**{
                    'weight': weight[selec],
                    name: df[hist['target']][selec].flatten()
                })

        return output

    def postprocess(self, accumulator):
        f = recreate(self.outfile)
        for h, hist in accumulator.items():
            f[h] = export1d(hist)
            print(f'wrote {h} to {self.outfile}')
        f.close()
        return accumulator

    def passbut(self, event: LazyDataFrame, excut: str, cat: str):
        """Backwards-compatible passbut."""
        return eval('&'.join('(' + cut.format(sys=('' if self.weight_syst else self.syst_suffix)) + ')'
                             for cut in self.selection[cat] if excut not in cut))

    def weighting(self, event: LazyDataFrame):
        return NotImplemented

    def naming_schema(self, *args):
        return NotImplemented


class MonoZ(WSProducer):
    histograms = {
        'h_bal': {
            'target': 'sca_balance',
            'name': 'balance',  # name to write to histogram
            'region': [
                'signal'
            ],
            'axis': {
                'label': 'sca_balance',  # fancy descriptive name
                'n_or_arr': 50,
                'lo': 0,
                'hi': 1
            }
        },
        'h_phi': {
            'target': 'delta_phi_ZMet',
            'name': 'phizmet',
            'region': [
                'signal'
            ],
            'axis': {
                'label': 'delta_phi_ZMet',
                'n_or_arr': 50,
                'lo': 0,
                'hi': 1
            }
        },
        'h_njet': {
            'target': 'ngood_jets',
            'name': 'njet',
            'region': [
                'signal'
            ],
            'axis': {
                'label': 'ngood_jets',
                'n_or_arr': 6,
                'lo': 0,
                'hi': 6
            }
        },
        'h1_measMET': {
            'target': 'met_pt',
            'name': 'measMET',
            'region': [
                'catSignal-0jet',
                'catEM',
                'catSignal-1jet',
            ],
            'axis': {
                'label': 'met_pt',
                'n_or_arr': [50, 100, 125, 150, 175, 200, 250, 300, 350, 400, 500, 600, 1000]
            }
        },
        'h2_measMET': {
            'target': 'met_pt',
            'name': 'measMET',
            'region': [
                'catNRB',
                'catTOP',
                'catDY'
            ],
            'axis': {
                'label': 'met_pt',
                'n_or_arr': [50, 60, 70, 80, 90, 100]
            }
        },
        'h_emulMET': {
            'target': 'emulatedMET',
            'name': 'measMET',
            'region': [
                'cat3L',
                'cat4L',
            ],
            'axis': {
                'label': 'met_pt',
                'n_or_arr': [50, 100, 125, 150, 175, 200, 250, 300, 350, 400, 500, 600, 1000]
            }
        },
        'h_mT': {
            'target': 'MT',
            'name': 'measMT',
            'region': [
                'catSignal-0jet',
                'catEM',
                'catSignal-1jet',
                'cat3L',
                'cat4L',
                'catNRB',
                'catTOP',
                'catDY'
            ],
            'axis': {
                'label': 'MET',
                'n_or_arr': [0, 100, 200, 250, 300, 350, 400, 500, 600, 700, 800, 1000, 1200, 2000]
            }
        }
    }
    selection = {
        "signal": [
            "event.Z_pt{sys}        >  60",
            "abs(event.Z_mass{sys} - 91.1876) < 15",
            "event.ngood_jets{sys}  <=  1",
            "event.ngood_bjets{sys} ==  0",
            "event.nhad_taus{sys}   ==  0",
            "event.met_pt{sys}      >  50",
            "abs(event.delta_phi_ZMet{sys} ) > 2.6",
            "abs(1 - event.sca_balance{sys}) < 0.4",
            "abs(event.delta_phi_j_met{sys}) > 0.5",
            "event.delta_R_ll{sys}           < 1.8"
        ],
        "cat3L": [
            "event.Z_pt{sys}        >  60",
            "abs(event.Z_mass{sys} - 91.1876) < 15",
            "event.ngood_jets{sys}  <=  1",
            "event.ngood_bjets{sys} ==  0",
            "event.met_pt{sys}      >  30",
            "event.mass_alllep{sys} > 100",
            "abs(1 -event.emulatedMET{sys}/event.Z_pt{sys}) < 0.4",
            "abs(event.emulatedMET_phi{sys} - event.Z_phi{sys}) > 2.6",
            "(event.lep_category{sys} == 4) | (event.lep_category{sys} == 5)",
        ],
        "cat4L": [
            "event.Z_pt{sys}        >  60",
            "abs(event.Z_mass{sys} - 91.1876) < 35",
            "event.ngood_jets{sys}  <=  1",
            "abs(event.emulatedMET_phi{sys} - event.Z_phi{sys}) > 2.6",
            "(event.lep_category{sys} == 6) | (event.lep_category{sys} == 7)",
        ],
        "catNRB": [
            "event.Z_pt{sys}        >  60",
            "abs(event.Z_mass{sys} - 91.1876) < 15",
            "event.ngood_jets{sys}  <=  1",
            "event.ngood_bjets{sys} ==  0",
            "event.met_pt{sys}      >  30"
        ],
        "catTOP": [
            "event.Z_pt{sys}        >  60",
            "abs(event.Z_mass{sys} - 91.1876) < 15",
            "event.ngood_jets{sys}  >   2",
            "event.ngood_bjets{sys} >=  1",
            "event.met_pt{sys}      >  30",
            "event.lep_category{sys} == 2"
        ],
        "catSignal-0jet": [
            "(event.lep_category{sys} == 1) | (event.lep_category{sys} == 3)",
            "event.ngood_jets{sys} == 0",
            "self.passbut(event, excut, 'signal')",
        ],
        "catSignal-1jet": [
            "(event.lep_category{sys} == 1) | (event.lep_category{sys} == 3)",
            "event.ngood_jets{sys} == 1",
            "self.passbut(event, excut, 'signal')",
        ],
        "catDY": [
            "(event.lep_category{sys} == 1) | (event.lep_category{sys} == 3)",
            "(event.ngood_jets{sys} == 0) | (event.ngood_jets{sys} == 1)",
            "self.passbut(event, excut, 'signal')",
        ],
        "catEM": [
            "event.lep_category{sys} == 2",
            "self.passbut(event, excut, 'catNRB')",
        ],
    }

    def weighting(self, event: LazyDataFrame):
        # cross-section
        weight = event.xsecscale

        # weight *= event.genWeight
        if "puWeight" in self.syst_var:
            if "Up" in self.syst_var:
                weight *= event.puWeightUp
            else:
                weight *= event.puWeightDown
        else:
            weight *= event.puWeight
        # Electroweak
        try:
            if "EWK" in self.syst_var:
                if "Up" in self.syst_var:
                    weight *= event.kEWUp
                else:
                    weight *= event.kEWDown
            else:
                weight *= event.kEW
        except:
            pass
        # NNLO crrection
        try:
            weight *= event.kNNLO
        except:
            pass
        # PDF uncertainty
        if "PDF" in self.syst_var:
            try:
                if "Up" in self.syst_var:
                    weight *= event.pdfw_Up
                else:
                    weight *= event.pdfw_Down
            except:
                pass
        # QCD Scale weights
        if "QCDScale0" in self.syst_var:
            try:
                if "Up" in self.syst_var:
                    weight *= event.QCDScale0wUp
                else:
                    weight *= event.QCDScale0wDown
            except:
                pass
        if "QCDScale1" in self.syst_var:
            try:
                if "Up" in self.syst_var:
                    weight *= event.QCDScale1wUp
                else:
                    weight *= event.QCDScale1wDown
            except:
                pass
        if "QCDScale2" in self.syst_var:
            try:
                if "Up" in self.syst_var:
                    weight *= event.QCDScale2wUp
                else:
                    weight *= event.QCDScale2wDown
            except:
                pass

        if "MuonSF" in self.syst_var:
            if "Up" in self.syst_var:
                weight *= event.w_muon_SFUp
            else:
                weight *= event.w_muon_SFDown
        else:
            weight *= event.w_muon_SF
        # Electron SF
        if "ElecronSF" in self.syst_var:
            if "Up" in self.syst_var:
                weight *= event.w_electron_SFUp
            else:
                weight *= event.w_electron_SFDown
        else:
            weight *= event.w_electron_SF
        # Prefire Weight
        try:
            if "PrefireWeight" in self.syst_var:
                if "Up" in self.syst_var:
                    weight *= event.PrefireWeight_Up
                else:
                    weight *= event.PrefireWeight_Down
            else:
                weight *= event.PrefireWeight
        except:
            pass
        # nvtx Weight
        if "nvtxWeight" in self.syst_var:
            if "Up" in self.syst_var:
                weight *= event.nvtxWeightUp
            else:
                weight *= event.nvtxWeightDown
        else:
            weight *= event.nvtxWeight
        # TriggerSFWeight
        if "TriggerSFWeight" in self.syst_var:
            if "Up" in self.syst_var:
                weight *= event.TriggerSFWeightUp
            else:
                weight *= event.TriggerSFWeightDown
        else:
            weight *= event.TriggerSFWeight
        # BTagEventWeight
        if "btagEventWeight" in self.syst_var:
            if "Up" in self.syst_var:
                weight *= event.btagEventWeightUp
            else:
                weight *= event.btagEventWeightDown
        else:
            weight *= event.btagEventWeight
        return weight

    def naming_schema(self, name, region):
        return f'{name}_{self.sample}_{region}{self.syst_suffix}'
