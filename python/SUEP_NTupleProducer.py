"""
WSProducer.py
Workspace producers using coffea.
"""
from coffea.hist import Hist, Bin, export1d
from coffea.processor import ProcessorABC, LazyDataFrame, dict_accumulator
from uproot import recreate
import numpy as np

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
        return accumulator

    def passbut(self, event: LazyDataFrame, excut: str, cat: str):
        """Backwards-compatible passbut."""
        return eval('&'.join('(' + cut.format(sys=('' if self.weight_syst else self.syst_suffix)) + ')' for cut in self.selection[cat] ))#if excut not in cut))

class SUEP_NTuple(WSProducer):
    histograms = {
        'h_nCleaned_Cands': {
            'target': 'nCleaned_Cands',
            'name': 'nCleaned_Cands',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'nCleaned_Cands', 'n_or_arr': 500, 'lo': 0, 'hi': 500}
        },
        'h_nPFCands': {
            'target': 'nPFCands',
            'name': 'nPFCands',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'nPFCands', 'n_or_arr': 800, 'lo': 0, 'hi': 800}
        },
        'h_met_pt': {
            'target': 'met_pt',
            'name': 'met_pt',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'met_pt', 'n_or_arr': 150, 'lo': 0, 'hi': 1500}
        },
        'h_CaloMET_pt': {
            'target': 'CaloMET_pt',
            'name': 'CaloMET_pt',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'CaloMET_pt', 'n_or_arr': 150, 'lo': 0, 'hi': 1500}
        },
        #'h_npv': {
        #    'target': 'npv',
        #    'name': 'npv',  # name to write to histogram
        #    'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
        #    'axis': {'label': 'npv', 'n_or_arr': 120, 'lo': 0, 'hi': 120}
        #},
        #'h_pu': {
        #    'target': 'pu',
        #    'name': 'pu',  # name to write to histogram
        #    'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
        #    'axis': {'label': 'pu', 'n_or_arr': 120, 'lo': 0, 'hi': 120}
        #},
        #'h_rho': {
        #    'target': 'rho',
        #    'name': 'rho',  # name to write to histogram
        #    'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
        #    'axis': {'label': 'rho', 'n_or_arr': 120, 'lo': 0, 'hi': 120}
        #},
        'h_SUEP_mult_pt': {
            'target': 'SUEP_mult_pt',
            'name': 'SUEP_mult_pt',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_mult_pt', 'n_or_arr': 100, 'lo': 0, 'hi': 2000}
        },
        'h_SUEP_mult_m': {
            'target': 'SUEP_mult_m',
            'name': 'SUEP_mult_m',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_mult_m', 'n_or_arr': 100, 'lo': 0, 'hi': 4000}
        },
        'h_SUEP_mult_eta': {
            'target': 'SUEP_mult_eta',
            'name': 'SUEP_mult_eta',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_mult_eta', 'n_or_arr': 100, 'lo': -5, 'hi': 5}
        },
        'h_SUEP_mult_phi': {
            'target': 'SUEP_mult_phi',
            'name': 'SUEP_mult_phi',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_mult_phi', 'n_or_arr': 100, 'lo': 0, 'hi': 6.5}
        },
        'h_SUEP_mult_nconst': {
            'target': 'SUEP_mult_nconst',
            'name': 'SUEP_mult_nconst',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_mult_nconst', 'n_or_arr': 800, 'lo': 0, 'hi': 800}
        },
        'h_SUEP_mult_spher': {
            'target': 'SUEP_mult_spher',
            'name': 'SUEP_mult_spher',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_mult_spher', 'n_or_arr': 100, 'lo': 0, 'hi': 1}
        },
        'h_SUEP_mult_aplan': {
            'target': 'SUEP_mult_aplan',
            'name': 'SUEP_mult_aplan',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_mult_aplan', 'n_or_arr': 100, 'lo': 0, 'hi': 1}
        },
        'h_SUEP_mult_FW2M': {
            'target': 'SUEP_mult_FW2M',
            'name': 'SUEP_mult_FW2M',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_mult_FW2M', 'n_or_arr': 100, 'lo': 0, 'hi': 1}
        },
        'h_SUEP_mult_D': {
            'target': 'SUEP_mult_D',
            'name': 'SUEP_mult_D',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_mult_D', 'n_or_arr': 100, 'lo': 0, 'hi': 1}
        },
        'h_SUEP_mult_pt_ave': {
            'target': 'SUEP_mult_pt_ave',
            'name': 'SUEP_mult_pt_ave',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_mult_pt_ave', 'n_or_arr': 100, 'lo': 0, 'hi': 25}
        },
        'h_SUEP_mult_girth': {
            'target': 'SUEP_mult_girth',
            'name': 'SUEP_mult_girth',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_mult_girth', 'n_or_arr': 30, 'lo': 0, 'hi': 3}
        },
        'h_SUEP_pt_pt': {
            'target': 'SUEP_pt_pt',
            'name': 'SUEP_pt_pt',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_pt_pt', 'n_or_arr': 100, 'lo': 0, 'hi': 2000}
        },
        'h_SUEP_pt_m': {
            'target': 'SUEP_pt_m',
            'name': 'SUEP_pt_m',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_pt_m', 'n_or_arr': 150, 'lo': 0, 'hi': 4000}
        },
        'h_SUEP_pt_eta': {
            'target': 'SUEP_pt_eta',
            'name': 'SUEP_pt_eta',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_pt_eta', 'n_or_arr': 100, 'lo': -5, 'hi': 5}
        },
        'h_SUEP_pt_phi': {
            'target': 'SUEP_pt_phi',
            'name': 'SUEP_pt_phi',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_pt_phi', 'n_or_arr': 100, 'lo': 0, 'hi': 6.5}
        },
        'h_SUEP_pt_nconst': {
            'target': 'SUEP_pt_nconst',
            'name': 'SUEP_pt_nconst',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_pt_nconst', 'n_or_arr': 800, 'lo': 0, 'hi': 800}
        },
        'h_SUEP_pt_spher': {
            'target': 'SUEP_pt_spher',
            'name': 'SUEP_pt_spher',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_pt_spher', 'n_or_arr': 100, 'lo': 0, 'hi': 1}
        },
        'h_SUEP_pt_aplan': {
            'target': 'SUEP_pt_aplan',
            'name': 'SUEP_pt_aplan',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_pt_aplan', 'n_or_arr': 100, 'lo': 0, 'hi': 1}
        },
        'h_SUEP_pt_FW2M': {
            'target': 'SUEP_pt_FW2M',
            'name': 'SUEP_pt_FW2M',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_pt_FW2M', 'n_or_arr': 100, 'lo': 0, 'hi': 1}
        },
        'h_SUEP_pt_D': {
            'target': 'SUEP_pt_D',
            'name': 'SUEP_pt_D',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_pt_D', 'n_or_arr': 100, 'lo': 0, 'hi': 1}
        },
        'h_SUEP_pt_pt_ave': {
            'target': 'SUEP_pt_pt_ave',
            'name': 'SUEP_pt_pt_ave',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_pt_pt_ave', 'n_or_arr': 100, 'lo': 0, 'hi': 25}
        },
        'h_SUEP_pt_girth': {
            'target': 'SUEP_pt_girth',
            'name': 'SUEP_pt_girth',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_pt_girth', 'n_or_arr': 30, 'lo': 0, 'hi': 3}
        },
        'h_SUEP_isr_pt': {
            'target': 'SUEP_isr_pt',
            'name': 'SUEP_isr_pt',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_isr_pt', 'n_or_arr': 100, 'lo': 0, 'hi': 2000}
        },  
        'h_SUEP_isr_m': {
            'target': 'SUEP_isr_m',
            'name': 'SUEP_isr_m',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_isr_m', 'n_or_arr': 150, 'lo': 0, 'hi': 4000}
        },
        'h_SUEP_isr_eta': {
            'target': 'SUEP_isr_eta',
            'name': 'SUEP_isr_eta',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_isr_eta', 'n_or_arr': 100, 'lo': -5, 'hi': 5}
        },
        'h_SUEP_isr_phi': {
            'target': 'SUEP_isr_phi',
            'name': 'SUEP_isr_phi',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_isr_phi', 'n_or_arr': 200, 'lo': -6.5, 'hi': 6.5}
        },
        'h_SUEP_isr_nconst': {
            'target': 'SUEP_isr_nconst',
            'name': 'SUEP_isr_nconst',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_isr_nconst', 'n_or_arr': 800, 'lo': 0, 'hi': 800}
        },
        'h_SUEP_isr_spher': {
            'target': 'SUEP_isr_spher',
            'name': 'SUEP_isr_spher',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_isr_spher', 'n_or_arr': 100, 'lo': 0, 'hi': 1}
        },
        'h_SUEP_isr_aplan': {
            'target': 'SUEP_isr_aplan',
            'name': 'SUEP_isr_aplan',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_isr_aplan', 'n_or_arr': 100, 'lo': 0, 'hi': 1}
        },
        'h_SUEP_isr_FW2M': {
            'target': 'SUEP_isr_FW2M',
            'name': 'SUEP_isr_FW2M',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_isr_FW2M', 'n_or_arr': 100, 'lo': 0, 'hi': 1}
        },
        'h_SUEP_isr_D': {
            'target': 'SUEP_isr_D',
            'name': 'SUEP_isr_D',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_isr_D', 'n_or_arr': 100, 'lo': 0, 'hi': 1}
        },
        'h_SUEP_isr_pt_ave': {
            'target': 'SUEP_isr_pt_ave',
            'name': 'SUEP_isr_pt_ave',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_isr_pt_ave', 'n_or_arr': 100, 'lo': 0, 'hi': 25}
        },
        'h_SUEP_isr_girth': {
            'target': 'SUEP_isr_girth',
            'name': 'SUEP_isr_girth',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'SUEP_isr_girth', 'n_or_arr': 30, 'lo': 0, 'hi': 3}
        },
        'h_HTTot': {
            'target': 'HTTot',
            'name': 'HTTot',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'HTTot', 'n_or_arr': 250, 'lo': 0, 'hi': 5000}
        },
        'h_ngood_fastjets': {
            'target': 'ngood_fastjets',
            'name': 'ngood_fastjets',  # name to write to histogram
            'region': ['basic', 'nconst_85', 'nconst_100', 'nconst_150', 'nconst_175', 'nconst_200', 'nconst_250'],
            'axis': {'label': 'ngood_fastjets', 'n_or_arr': 15, 'lo': 0, 'hi': 15}
        },
    }
    selection = {
            "basic" : [
                "event.met_filter{sys}==1" ,
		#"(event.HLT_PFHT1050{sys}==1) | (event.HLT_PFJet500{sys}==1)",
	    ],
            "nconst_85" : [
                "event.met_filter{sys}==1" ,
                #"(event.HLT_PFHT1050{sys}==1) | (event.HLT_PFJet500{sys}==1)",
		"event.nCleaned_Cands{sys} > 85"
            ],
            "nconst_100" : [
                "event.met_filter{sys}==1" ,
                #"(event.HLT_PFHT1050{sys}==1) | (event.HLT_PFJet500{sys}==1)",
                "event.nCleaned_Cands{sys} > 100"
            ],
            "nconst_150" : [
                "event.met_filter{sys}==1" ,
                #"(event.HLT_PFHT1050{sys}==1) | (event.HLT_PFJet500{sys}==1)",
                "event.nCleaned_Cands{sys} > 150"
            ],
            "nconst_175" : [
                "event.met_filter{sys}==1" ,
                #"(event.HLT_PFHT1050{sys}==1) | (event.HLT_PFJet500{sys}==1)",
                "event.nCleaned_Cands{sys} > 175"
            ],
            "nconst_200" : [
                "event.met_filter{sys}==1" ,
                #"(event.HLT_PFHT1050{sys}==1) | (event.HLT_PFJet500{sys}==1)",
                "event.nCleaned_Cands{sys} > 200"
            ],
            "nconst_250" : [
                "event.met_filter{sys}==1" ,
               # "(event.HLT_PFHT1050{sys}==1) | (event.HLT_PFJet500{sys}==1)",
                "event.nCleaned_Cands{sys} > 250"
            ],
        }


    def weighting(self, event: LazyDataFrame):
        weight = 1.0
        try:
            weight = event.xsecscale
        except:
            return "ERROR: weight branch doesn't exist"
        return weight

    def naming_schema(self, name, region):
        return f'{name}_{self.sample}_{region}{self.syst_suffix}'
