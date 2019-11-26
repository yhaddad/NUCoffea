#!/bin/env python3
import pickle
from re import findall

import coffea.processor as processor
import matplotlib.pyplot as plt
import numpy as np
from coffea import hist

from .dataset_finder import get_datasets, locate_root_files
from .workspace import MonoZMuMuProducer

from . import physics_mplstyle
plt.style.use(physics_mplstyle)


def plot_MT(cat, bins, s=None):
    fig, ax = plt.subplots(1, 1, figsize=(7, 7))
    all_ = output['MT1'].integrate('region', f'cat_{cat}').copy()
    all_ = all_.rebin("MT1", hist.Bin("MT1" + "_new", 50, np.linspace(0, bins, 51)))
    #allb_ = output['MT1'].integrate('region', f'all_{cat}').copy()
    #allb_ = allb_.rebin("MT1", hist.Bin("MT1" + "_new", 50, np.linspace(0, bins, 51)))
    if s:
        # patch histogram to use subset of datasets.
        new_sumw = {key:all_._sumw[key] for key in all_._sumw if str(key[0]) in s}
        #new_sumwb = {(hist.StringBin(f"{str(key[0])}-back"),):allb_._sumw[key] for key in allb_._sumw if str(key[0]) in s}
        #new_sumw.update(new_sumwb)
        all_._sumw = new_sumw
        #all_._axes[0]._sorted = list(s) + list(f"{i}-back" for i in s)
        #all_._axes[0]._bins = {key: hist.StringBin(key) for key in all_._axes[0]._sorted}
    hist.plot1d(
        all_, overlay='dataset', ax=ax,
        # stack=True
    )
    ax.text(0.0,1.02,r'$\mathbf{CMS}~\mathit{Preliminary}$', fontsize=15, transform=ax.transAxes)
    ax.text(1.0,1.02,r'60.0 $\mathrm{fb}^{-1}$ (13 TeV 2018)', fontsize=12, horizontalalignment='right', transform=ax.transAxes)
    ax.set_xlabel(r"$M_T$ (GeV)", horizontalalignment='right', x=1.0)
    ax.set_yscale("log")
    ax.set_ylim([0.1, 90000])
    fig.savefig(f'MT_{cat}_{bins}.png')
    del fig

def plot_MET(cat, bins, s=None):
    fig, ax = plt.subplots(1, 1, figsize=(7, 7))
    all_ = output['MET'].integrate('region', f'cat_{cat}').copy()
    all_ = all_.rebin("MET", hist.Bin("MET" + "_new", 50, np.linspace(0, bins, 51)))
    #allb_ = output['MT1'].integrate('region', f'all_{cat}').copy()
    #allb_ = allb_.rebin("MT1", hist.Bin("MT1" + "_new", 50, np.linspace(0, bins, 51)))
    if s:
        # patch histogram to use subset of datasets.
        new_sumw = {key:all_._sumw[key] for key in all_._sumw if str(key[0]) in s}
        #new_sumwb = {(hist.StringBin(f"{str(key[0])}-back"),):allb_._sumw[key] for key in allb_._sumw if str(key[0]) in s}
        #new_sumw.update(new_sumwb)
        all_._sumw = new_sumw
        #all_._axes[0]._sorted = list(s) + list(f"{i}-back" for i in s)
        #all_._axes[0]._bins = {key: hist.StringBin(key) for key in all_._axes[0]._sorted}
    hist.plot1d(
        all_, overlay='dataset', ax=ax,
        # stack=True
    )
    ax.text(0.0,1.02,r'$\mathbf{CMS}~\mathit{Preliminary}$', fontsize=15, transform=ax.transAxes)
    ax.text(1.0,1.02,r'60.0 $\mathrm{fb}^{-1}$ (13 TeV 2018)', fontsize=12, horizontalalignment='right', transform=ax.transAxes)
    ax.set_xlabel(r"MET (GeV)", horizontalalignment='right', x=1.0)
    ax.set_yscale("log")
    ax.set_ylim([0.1, 90000])
    fig.savefig(f'MET_{cat}_{bins}.png')

def plot_efficiency_MT(cat, s):
    plt.figure()
    for i in s:
        all_ = output['MT1'].integrate('region', f'all_{cat}')._axes[1]._intervals[1].hi - \
               output['MT1'].integrate('region', f'all_{cat}')._axes[1]._intervals[1].lo
        all = output['MT1'].integrate('region', f'all_{cat}').values()[(i,)]
        sig = output['MT1'].integrate('region', f'cat_{cat}').values()[(i,)]
        plt.plot(list(range(0, int(len(all)*all_), int(all_))), np.divide(sig, all, where=all != 0))
    plt.gca().set_xlim([0, 600])
    plt.gca().set_xlabel('MT (GeV)')
    plt.gca().set_ylabel('Efficiency')
    plt.legend(s)
    plt.savefig('test.png')



def plot_sensitivities(variables, cat):
    def calculate(variable):
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

    results = [calculate(v) for v in variables]
    linestyles = ["r.--", "b.--"]

    plt.figure(figsize=(12, 4))
    names = [str(v[0]) + "-" + str(v[1]) for v in results[0]]
    for i, r in enumerate(results):
        plt.plot(names, r[:, 2], linestyles[i], ms=12, label=variables[i])
    plt.tight_layout()
    plt.grid(b=True, which='major', color='grey', linestyle='--', alpha=0.3)
    plt.minorticks_off()
    plt.xticks(names, names, rotation='vertical')
    plt.legend(fontsize=14)
    plt.tight_layout()
    plt.savefig('sensitivity.png')


def plot_efficiencies(variables, cat):
    def calculate(variable):
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

    results = [calculate(v) for v in variables]
    linestyles = ["r.--", "b.--"]

    plt.figure(figsize=(12, 4))
    names = [str(v[0]) + "-" + str(v[1]) for v in results[0]]
    for i, r in enumerate(results):
        plt.plot(names, r[:, 2], linestyles[i], ms=12, label=variables[i])
    plt.tight_layout()
    plt.grid(b=True, which='major', color='grey', linestyle='--', alpha=0.3)
    plt.minorticks_off()
    plt.xticks(names, names, rotation='vertical')
    plt.legend(fontsize=14)
    plt.tight_layout()
    plt.savefig('efficiency.png')


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

    for cat in ['0j', '1j', '01j']:
        for bins in [1000, 2000]:
            for h in [2]:
                s = [f"Pseudoscalar_mH-{h}00_ma-{a}00" for a in range(1,5)] + ['bkg']
                plot_MT(cat, bins, s=s)
        variables = ['MET', 'MT1']
        plot_sensitivities(variables, cat)
        plot_efficiencies(variables, cat)
        plot_MT(cat, 1000, s=("Pseudoscalar_mH-200_ma-100",
                              "Pseudoscalar_mH-300_ma-100",
                              "Pseudoscalar_mH-400_ma-100",
                              "Pseudoscalar_mH-500_ma-100",
                              "Pseudoscalar_mH-600_ma-100",
                              "Pseudoscalar_mH-700_ma-100",
                              "Pseudoscalar_mH-800_ma-100",
                              "bkg",
                              "TT","ST","WZTo","WWTo","ZZTo", "ZZZ", "WWZ", "WZZ", "JetsToLL_M"))
        plot_MET(cat, 1000, s=("Pseudoscalar_mH-200_ma-100",
                              "Pseudoscalar_mH-300_ma-100",
                              "Pseudoscalar_mH-400_ma-100",
                              "Pseudoscalar_mH-500_ma-100",
                              "Pseudoscalar_mH-600_ma-100",
                              "Pseudoscalar_mH-700_ma-100",
                              "Pseudoscalar_mH-800_ma-100",
                              "bkg",
                              "TT","ST","WZTo","WWTo","ZZTo", "ZZZ", "WWZ", "WZZ", "JetsToLL_M"))
        plot_efficiency_MT(cat, s=("Pseudoscalar_mH-200_ma-100",
                              "Pseudoscalar_mH-300_ma-100",
                              "Pseudoscalar_mH-400_ma-100",
                              "Pseudoscalar_mH-500_ma-100",
                              "Pseudoscalar_mH-600_ma-100",
                              "Pseudoscalar_mH-700_ma-100",
                              "Pseudoscalar_mH-800_ma-100",))