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
                    #'weight': weight[selec],
                    name: df[hist['target']][selec].flatten()
                })

        return output

    def postprocess(self, accumulator):
        return accumulator

    def passbut(self, event: LazyDataFrame, excut: str, cat: str):
        """Backwards-compatible passbut."""
        return eval('&'.join('(' + cut.format(sys=('' if self.weight_syst else self.syst_suffix)) + ')'
                             for cut in self.selection[cat] if excut not in cut))

class SUEP(WSProducer):
    histograms = {
        'h_PFCands_d0': {
            'target': 'PFCands_d0',
            'name': 'PF Candidate d0',  # name to write to histogram
            'region': ['signal'],
            'axis': {'label': 'PF Candidate d0', 'n_or_arr': 100, 'lo': 0, 'hi': 0.5}
        },
        'h_PFCands_d0Err': {
            'target': 'PFCands_d0Err',
            'name': 'PF Candidate d0Err',  # name to write to histogram
            'region': ['signal'],
            'axis': {'label': 'PF Candidate d0Err', 'n_or_arr': 100, 'lo': 0, 'hi': 0.5}
        },
        'h_PFCands_dz': {
            'target': 'PFCands_dz',
            'name': 'PF Candidate dz',  # name to write to histogram
            'region': ['signal'],
            'axis': {'label': 'PF Candidate dz', 'n_or_arr': 100, 'lo': 0, 'hi': 10}
        },
        'h_PFCands_dzErr': {
            'target': 'PFCands_dzErr',
            'name': 'PF Candidate dzErr',  # name to write to histogram
            'region': ['signal'],
            'axis': {'label': 'PF Candidate dzErr', 'n_or_arr': 100, 'lo': 0, 'hi': 10}
        },
        'h_PFCands_eta': {
            'target': 'PFCands_eta',
            'name': 'PF Candidate eta',  # name to write to histogram
            'region': ['signal'],
            'axis': {'label': 'PF Candidate eta', 'n_or_arr': 100, 'lo': -5, 'hi': 5}
        },
        'h_PFCands_mass': {
            'target': 'PFCands_mass',
            'name': 'PF Candidate mass',  # name to write to histogram
            'region': ['signal'],
            'axis': {'label': 'PF Candidate mass', 'n_or_arr': 100, 'lo': 0, 'hi': 5}
        },
        'h_PFCands_phi': {
            'target': 'PFCands_phi',
            'name': 'PF Candidate phi',  # name to write to histogram
            'region': ['signal'],
            'axis': {'label': 'PF Candidate phi', 'n_or_arr': 100, 'lo': -4, 'hi': 4}
        },
        'h_PFCands_pt': {
            'target': 'PFCands_pt',
            'name': 'PF Candidate pt',  # name to write to histogram
            'region': ['signal'],
            'axis': {'label': 'PF Candidate pt', 'n_or_arr': 100, 'lo': 0, 'hi': 10}
        },
        'h_PFCands_trkChi2': {
            'target': 'PFCands_trkChi2',
            'name': 'PF Candidate trkChi2',  # name to write to histogram
            'region': ['signal'],
            'axis': {'label': 'PF Candidate trkChi2', 'n_or_arr': 100, 'lo': 0, 'hi': 100}
        },
        'h_PFCands_trkEta': {
            'target': 'PFCands_trkEta',
            'name': 'PF Candidate trkEta',  # name to write to histogram
            'region': ['signal'],
            'axis': {'label': 'PF Candidate trkEta', 'n_or_arr': 100, 'lo': -5, 'hi': 5}
        },
        'h_PFCands_trkPhi': {
            'target': 'PFCands_trkPhi',
            'name': 'PF Candidate trkPhi',  # name to write to histogram
            'region': ['signal'],
            'axis': {'label': 'PF Candidate trkPhi', 'n_or_arr': 100, 'lo': -4, 'hi': 4}
        },

        'h_PFCands_trkPt': {
            'target': 'PFCands_trkPt',
            'name': 'PF Candidate trkPt',  # name to write to histogram
            'region': ['signal'],
            'axis': {'label': 'PF Candidate trkPt', 'n_or_arr': 100, 'lo': 0, 'hi': 10}
        },
        'h_PFCands_vtxChi2': {
            'target': 'PFCands_vtxChi2',
            'name': 'PF Candidate vtxChi2',  # name to write to histogram
            'region': ['signal'],
            'axis': {'label': 'PF Candidate vtxChi2', 'n_or_arr': 100, 'lo': 0, 'hi': 10}
        },
    }
    selection = {
            "signal" : [
                "event.HLT_PFHT250==1" ,
	    ]
        }


    def weighting(self, event: LazyDataFrame):
        weight = 1.0
        return weight

    def naming_schema(self, name, region):
        return f'{name}_{self.sample}_{region}{self.syst_suffix}'
