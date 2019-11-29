#!/bin/env python3
import pickle
from re import findall

import coffea.processor as processor
import numpy as np
from coffea import hist

from .dataset_finder import get_datasets, locate_root_files
from .util import CMSPreliminary
from .workspace import MonoZMuMuProducer


def variable_histogram_plot(kind):
    def generic(cat, bins, s=None):
        variable, label = kind()
        with CMSPreliminary(label, "Events", 2018, figsize=(7, 7)) as ax:
            all_ = output[variable].integrate('region', f'cat_{cat}').copy()
            all_ = all_.rebin(variable, hist.Bin(variable + "_new", 50, np.linspace(0, bins, 51)))
            # allb_ = output[variable].integrate('region', f'all_{cat}').copy()
            # allb_ = allb_.rebin(variable, hist.Bin(variable + "_new", 50, np.linspace(0, bins, 51)))
            if s:
                # patch histogram to use subset of datasets.
                new_sumw = {key: all_._sumw[key] for key in all_._sumw if str(key[0]) in s}
                # new_sumwb = {(hist.StringBin(f"{str(key[0])}-back"),):allb_._sumw[key] for key in allb_._sumw if str(key[0]) in s}
                # new_sumw.update(new_sumwb)
                all_._sumw = new_sumw
                # all_._axes[0]._sorted = list(s) + list(f"{i}-back" for i in s)
                # all_._axes[0]._bins = {key: hist.StringBin(key) for key in all_._axes[0]._sorted}
            hist.plot1d(
                all_, overlay='dataset', ax=ax,
                # stack=True
            )
            ax.set_yscale("log")
            ax.set_ylim([0.1, 90000])
        ax.savefig(f'{variable}_{cat}_{bins}.png')

    return generic


def by_dataset_plot(kind):
    def generic(variables, cat):
        calculate, axis_labels = kind()
        results = [calculate(v, cat) for v in variables]
        names = ['$m_H$ $m_a$'] + [f'{v[0] / 100:2.0f}  {v[1] / 100:2.0f}' for v in results[0]]
        linestyles = ["r.--", "b.--"]
        with CMSPreliminary(*axis_labels, 2018, figsize=(12, 4)) as ax:
            for i, r in enumerate(results):
                ax.plot(names, [np.NaN] + list(r[:, 2]), linestyles[i], ms=12, label=variables[i])
            ax.grid(b=True, which='major', color='grey', linestyle='--', alpha=0.3)
            ax.minorticks_off()
            ax.set_xticks(names, names)
            ax.xaxis.set_tick_params(rotation=90)
            ax.legend(fontsize=14)
            ax.set_xlim(0, len(names))
        ax.savefig(f'{axis_labels[1].lower()}_{"-".join(variables)}_{cat}.png')

    return generic


@variable_histogram_plot
def plot_MT():
    return 'MT1', '$M_T$ (GeV)'


@variable_histogram_plot
def plot_MET():
    return 'MET', 'MET (GeV)'


@by_dataset_plot
def plot_sensitivities():
    def calculate(variable, cat):
        def sig_value(s, b):
            # sign = 2*((s+b)*np.log(1 + np.divide(s,b, where=b!=0)) - s)
            sign = np.divide(s ** 2, b, where=b != 0)
            return np.sqrt(np.sum(sign))

        bkg = output[variable].integrate('region', f'cat_{cat}').values()[("bkg",)]
        results = []
        mH = []
        ma = []
        for s in (i[0] for i in output[variable].integrate('region', f'cat_{cat}').values().keys()):
            if "Pseudoscalar" not in s: continue
            sig = output[variable].integrate('region', f'cat_{cat}').values()[(s,)]
            results.append(sig_value(sig, bkg))
            mH_, ma_ = [int(i) for i in findall(r'\d+', s)]
            mH.append(mH_)
            ma.append(ma_)
            # print("%20s : %1.3f" % (s, sig_value(sig, bkg)) )
        a = np.array([mH, ma, results]).T
        i = np.lexsort((a[:, 1], a[:, 0]))
        return a[i]

    return calculate, (r'Normalized sensitivity of variables by dataset $m_H$, $m_a$ ($\times100$ GeV/$c^2$)',
                       'Sensitivity')


@by_dataset_plot
def plot_efficiencies():
    def calculate(variable, cat):
        results = []
        mH = []
        ma = []
        for s in (i[0] for i in output[variable].integrate('region', f'all_{cat}').values().keys()):
            if "Pseudoscalar" not in s: continue
            all = list(output[variable].integrate('region', f'all_{cat}').values()[(s,)])
            sig = list(output[variable].integrate('region', f'cat_{cat}').values()[(s,)])
            results.append(np.divide(np.sum(sig), np.sum(all)))
            mH_, ma_ = [int(i) for i in findall(r'\d+', s)]
            mH.append(mH_)
            ma.append(ma_)
            # print("%20s : %1.3f" % (s, sig_value(sig, bkg)) )
        a = np.array([mH, ma, results]).T
        i = np.lexsort((a[:, 1], a[:, 0]))
        return a[i]

    return calculate, (r'Efficiency of 2HDM+a / MonoZ selections by dataset $m_H$, $m_a$ ($\times100$ GeV/$c^2$)',
                       'Efficiency')


def plot_efficiency_MT(cat, s):
    with CMSPreliminary('MT', "Efficiency", 2018, figsize=(7, 7)) as ax:
        for i in s:
            all_ = output['MT1'].integrate('region', f'all_{cat}')._axes[1]._intervals[1].hi - \
                   output['MT1'].integrate('region', f'all_{cat}')._axes[1]._intervals[1].lo
            all = output['MT1'].integrate('region', f'all_{cat}').values()[(i,)]
            sig = output['MT1'].integrate('region', f'cat_{cat}').values()[(i,)]
            ax.plot(list(range(0, int(len(all) * all_), int(all_))), np.divide(sig, all, where=all != 0))
        ax.set_xlim([0, 600])
        ax.legend(s)
    ax.savefig('test.png')


if __name__ == '__main__':
    locate_root_files()
    datasets = get_datasets()
    try:
        with open('output.pkl', 'rb') as f:
            output = pickle.load(f)
    except FileNotFoundError:
        output = processor.run_uproot_job(
            datasets,
            treename='Events',
            processor_instance=MonoZMuMuProducer(),
            executor=processor.futures_executor,
            executor_args={'workers': 10},
            chunksize=500000
        )
        with open('output.pkl', 'wb') as f:
            pickle.dump(output, f)

    for g_cat in ['0j', '1j', '01j']:
        # for bins in [1000, 2000]:
        #     for h in [2]:
        #         s = [f"Pseudoscalar_mH-{h}00_ma-{a}00" for a in range(1, 5)] + ['bkg']
        #         plot_MT(g_cat, bins, s=s)
        variables = ['MET', 'MT1']
        plot_sensitivities(variables, g_cat)
        plot_efficiencies([variables[0]], g_cat)
        plot_MT(g_cat, 1000, s=("Pseudoscalar_mH-200_ma-100",
                                "Pseudoscalar_mH-300_ma-100",
                                "Pseudoscalar_mH-400_ma-100",
                                "Pseudoscalar_mH-500_ma-100",
                                "Pseudoscalar_mH-600_ma-100",
                                "Pseudoscalar_mH-700_ma-100",
                                "Pseudoscalar_mH-800_ma-100",
                                "bkg",))
        # "TT", "ST", "WZTo", "WWTo", "ZZTo", "ZZZ", "WWZ", "WZZ", "JetsToLL_M"))
        plot_MET(g_cat, 1000, s=("Pseudoscalar_mH-200_ma-100",
                                 "Pseudoscalar_mH-300_ma-100",
                                 "Pseudoscalar_mH-400_ma-100",
                                 "Pseudoscalar_mH-500_ma-100",
                                 "Pseudoscalar_mH-600_ma-100",
                                 "Pseudoscalar_mH-700_ma-100",
                                 "Pseudoscalar_mH-800_ma-100",
                                 "bkg",))
        # "TT", "ST", "WZTo", "WWTo", "ZZTo", "ZZZ", "WWZ", "WZZ", "JetsToLL_M"))
        # plot_efficiency_MT(g_cat, s=("Pseudoscalar_mH-200_ma-100",
        #                              "Pseudoscalar_mH-300_ma-100",
        #                              "Pseudoscalar_mH-400_ma-100",
        #                              "Pseudoscalar_mH-500_ma-100",
        #                              "Pseudoscalar_mH-600_ma-100",
        #                              "Pseudoscalar_mH-700_ma-100",
        #                              "Pseudoscalar_mH-800_ma-100",))
