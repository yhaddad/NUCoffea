"""
Producer classes.
"""
import os

import coffea.processor as processor
import numpy as np
import yaml
from coffea import hist

from .util import d_phi


class MonoZMuMuProducer(processor.ProcessorABC):
    def __init__(self, era=2018):
        datasets_axis = hist.Cat("dataset", "Signal Model")
        category_axis = hist.Cat("region", "Lepton category")
        sys_axis = hist.Cat("syst", "systematic variation")
        MT1_axis = hist.Bin("MT1", r"$M_{T,1}$ [GeV]", 500, 0, 2000)
        MT2_axis = hist.Bin("MT2", r"$M_{T,2}$ [GeV]", 500, 0, 2000)
        MT3_axis = hist.Bin("MT3", r"$M_{T,3}$ [GeV]", 500, 0, 2000)
        ST1_axis = hist.Bin("ST1", r"$S_{T,1}$ [GeV]", 500, 0, 2000)
        MET_axis = hist.Bin("MET", r"$E_{T}^{miss}$ [GeV]", 500, 0, 2000)
        RT1_axis = hist.Bin("RT1", r"$R_{T}$", 500, 0, 200)

        self._accumulator = processor.dict_accumulator({
            'MET': hist.Hist("Events", datasets_axis, category_axis, MET_axis),
            'MT1': hist.Hist("Events", datasets_axis, category_axis, MT1_axis),
            'MT2': hist.Hist("Events", datasets_axis, category_axis, MT2_axis),
            'MT3': hist.Hist("Events", datasets_axis, category_axis, MT3_axis),
            'RT1': hist.Hist("Events", datasets_axis, category_axis, RT1_axis),
            'cutflow': processor.defaultdict_accumulator(int),
        })

        with open(f"{os.path.dirname(__file__)}/xsections_{era}.yaml") as stream:
            self.xsections = yaml.safe_load(stream)
        self.lumi = {
            2016: 35.9,
            2017: 41.5,
            2018: 60.0
        }[era]

    @property
    def accumulator(self):
        return self._accumulator

    def process(self, df, work_function_vars):
        output = self.accumulator.identity()
        dataset = df['dataset']

        # get the lepton category
        lepcat = df["lep_category"]
        df["category_tag"] = "none"

        emulatedMET_phi = df["emulatedMET_phi"]
        emul_d_phi_ZMet = d_phi(df["emulatedMET_phi"], df["Z_phi"])

        # select at least two leptons, and then OC
        selection = dict(
            cat_0j=(
                    ((lepcat == 1) | (lepcat == 3)) &
                    (df["met_pt"] > 50) & (df["Z_pt"] > 60) &
                    (np.abs(df["Z_mass"] - 91.1876) < 15) &
                    # (np.abs(df["delta_phi_ZMet"])  > 2.6) &
                    # (np.abs(1 - df["sca_balance"]) < 0.4) &
                    # (np.abs(df["delta_phi_j_met"]) > 0.5) &
                    (df["delta_R_ll"] < 1.8) &
                    (df["nhad_taus"] == 0) &
                    (df["ngood_bjets"] == 0) &
                    (df["ngood_jets"] == 0)
            ),
            all_0j=(
                    ((lepcat == 1) | (lepcat == 3)) &
                    (df["nhad_taus"] == 0) &
                    (df["ngood_bjets"] == 0) &
                    (df["ngood_jets"] == 0)
            ),
            cat_1j=(
                    ((lepcat == 1) | (lepcat == 3)) &
                    (df["met_pt"] > 50) & (df["Z_pt"] > 60) &
                    (np.abs(df["Z_mass"] - 91.1876) < 15) &
                    # (np.abs(df["delta_phi_ZMet"])  > 2.6) &
                    # (np.abs(1 - df["sca_balance"]) < 0.4) &
                    # (np.abs(df["delta_phi_j_met"]) > 0.5) &
                    (df["delta_R_ll"] < 1.8) &
                    (df["nhad_taus"] == 0) &
                    (df["ngood_bjets"] == 0) &
                    (df["ngood_jets"] == 1)
            ),
            all_1j=(
                    (df["nhad_taus"] == 0) &
                    (df["ngood_bjets"] == 0) &
                    (df["ngood_jets"] == 1)
            ),
            cat_EM=(
                    (lepcat == 2) &
                    (df["met_pt"] > 50) & (df["Z_pt"] > 60) &
                    (np.abs(df["Z_mass"] - 91.1876) < 15) &
                    # (np.abs(df["delta_phi_ZMet"])  > 2.6) &
                    # (np.abs(1 - df["sca_balance"]) < 0.4) &
                    # (np.abs(df["delta_phi_j_met"]) > 0.5) &
                    (df["delta_R_ll"] < 1.8) &
                    (df["nhad_taus"] == 0) &
                    (df["ngood_bjets"] == 0) &
                    (df["ngood_jets"] <= 1)
            ),
            cat_3L=(
                    ((lepcat == 4) | (lepcat == 5)) &
                    (df["met_pt"] > 50) & (df["Z_pt"] > 60) &
                    (np.abs(df["Z_mass"] - 91.1876) < 15) &
                    # (np.abs(emul_d_phi_ZMet)  > 2.6) &
                    # (np.abs(1 - df["sca_balance"]) < 0.4) &
                    (df["mass_alllep"] > 100) &
                    (df["ngood_bjets"] == 0) &
                    (df["ngood_jets"] <= 1)
            ),
            cat_4L=(
                    ((lepcat == 6) | (lepcat == 7)) &
                    (df["met_pt"] > 30) & (df["Z_pt"] > 60) &
                    # (np.abs(emul_d_phi_ZMet)  > 2.6) &
                    (df["ngood_jets"] <= 1)
            ))

        selection['cat_01j'] = selection['cat_0j'] | selection['cat_1j']
        selection['all_01j'] = selection['all_0j'] | selection['all_1j']

        weight = df['puWeight']
        weight *= df['w_muon_SF']
        weight *= df['w_electron_SF']
        # weight *= df['PrefireWeight']
        weight *= df['nvtxWeight']
        weight *= df['TriggerSFWeight']
        weight *= df['btagEventWeight']
        scale = self.lumi / work_function_vars['file']["Runs"].array("genEventCount").sum()
        dataset_name = os.path.basename(os.path.dirname(work_function_vars['item'].filename.replace(".root", "")))
        xsec = self.xsections[dataset_name]["xsec"]
        xsec *= self.xsections[dataset_name]["kr"]
        xsec *= self.xsections[dataset_name]["br"]
        xsec *= 1000.0
        scale *= xsec
        weight *= scale
        for cat in list(selection.keys()):
            meas_MET = np.where(
                lepcat >= 4, df["emulatedMET"], df["met_pt"]
            )
            meas_MT1 = df["MT"]

            meas_MT2 = np.sqrt(
                np.power(
                    np.sqrt(np.power(df["Z_pt"], 2) + np.power(df["Z_mass"], 2)) +
                    np.sqrt(np.power(df["met_pt"], 2) + np.power(df["Z_mass"], 2)), 2
                ) - (
                        np.power(df["Z_pt"], 2) + np.power(df["met_pt"], 2) + 2 * df["Z_pt"] * df["met_pt"] * np.cos(
                    df["delta_phi_ZMet"])
                )
            )

            output['MET'].fill(dataset=dataset, region=cat, MET=meas_MET[selection[cat]].flatten(),
                               weight=weight[selection[cat]])
            output['MT1'].fill(dataset=dataset, region=cat, MT1=meas_MT1[selection[cat]].flatten(),
                               weight=weight[selection[cat]])
            output['MT2'].fill(dataset=dataset, region=cat, MT2=meas_MT2[selection[cat]].flatten(),
                               weight=weight[selection[cat]])
        return output

    def postprocess(self, accumulator):
        return accumulator
