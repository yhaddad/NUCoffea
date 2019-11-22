#!/bin/env python3
import os

import yaml

dir_monoZ = '/eos/cms/store/group/phys_exotica/monoZ/redemption2018/'


def locate_root_files():
    """Locates selected root files containing data and writes a yaml file with paths."""
    dict_files = {}
    print(('Walking through directory:', dir_monoZ))
    for path, subdirs, files in os.walk(dir_monoZ):
        sub_path_splited = path.split(dir_monoZ)[1].split('/')
        dataset = sub_path_splited[0]
        if len(dataset) == 0:
            continue
        # if "DMSimp" in dataset: continue
        # if "2HDM"   in dataset: continue
        # if "Unpart" in dataset: continue
        if "merged" in dataset:
            continue
        # print("sub_path_splited : ", sub_path_splited)
        if dataset not in dict_files:
            dict_files[dataset] = []
        for name in files:
            if name.split('.')[-1] == 'root':
                dict_files[dataset].append(os.path.join(path, name))

    with open('ROOTfiles.yml', 'w') as outfile:
        yaml.dump(dict_files, outfile, default_flow_style=False)


def get_datasets():
    """loads datasets."""
    with open("ROOTfiles.yml", 'r') as stream:
        fileset = yaml.safe_load(stream)

    import itertools

    def merged_dataset(pattern="JetsToLL_M"):
        vec = [n for i, n in list(fileset.items()) if pattern in i]
        vec = list(itertools.chain(*vec))
        return vec

    return {
        #     "data"   : merged_dataset(pattern="Run2017"),
        "bkg": (merged_dataset(pattern="TT") + merged_dataset(pattern="ST") +
                merged_dataset(pattern="WZTo") + merged_dataset(pattern="WWTo") +
                merged_dataset(pattern="ZZTo") + merged_dataset(pattern="ZZZ") + merged_dataset(pattern="WWZ") +
                merged_dataset(pattern="WZZ") + merged_dataset(pattern="JetsToLL_M")),

        "Pseudoscalar_mH-1000_ma-100": merged_dataset(pattern="mH-1000_ma-100"),
        "Pseudoscalar_mH-1000_ma-200": merged_dataset(pattern="mH-1000_ma-200"),
        "Pseudoscalar_mH-1000_ma-300": merged_dataset(pattern="mH-1000_ma-300"),
        "Pseudoscalar_mH-1000_ma-400": merged_dataset(pattern="mH-1000_ma-400"),
        "Pseudoscalar_mH-1000_ma-500": merged_dataset(pattern="mH-1000_ma-500"),
        "Pseudoscalar_mH-1200_ma-100": merged_dataset(pattern="mH-1200_ma-100"),
        "Pseudoscalar_mH-1200_ma-200": merged_dataset(pattern="mH-1200_ma-200"),
        "Pseudoscalar_mH-1200_ma-300": merged_dataset(pattern="mH-1200_ma-300"),
        "Pseudoscalar_mH-1200_ma-400": merged_dataset(pattern="mH-1200_ma-400"),
        "Pseudoscalar_mH-1200_ma-500": merged_dataset(pattern="mH-1200_ma-500"),
        "Pseudoscalar_mH-1400_ma-100": merged_dataset(pattern="mH-1400_ma-100"),
        "Pseudoscalar_mH-1400_ma-200": merged_dataset(pattern="mH-1400_ma-200"),
        "Pseudoscalar_mH-1400_ma-300": merged_dataset(pattern="mH-1400_ma-300"),
        "Pseudoscalar_mH-1400_ma-400": merged_dataset(pattern="mH-1400_ma-400"),
        "Pseudoscalar_mH-1400_ma-500": merged_dataset(pattern="mH-1400_ma-500"),
        "Pseudoscalar_mH-200_ma-100": merged_dataset(pattern="mH-200_ma-100"),
        "Pseudoscalar_mH-300_ma-100": merged_dataset(pattern="mH-300_ma-100"),
        "Pseudoscalar_mH-300_ma-200": merged_dataset(pattern="mH-300_ma-200"),
        "Pseudoscalar_mH-400_ma-100": merged_dataset(pattern="mH-400_ma-100"),
        "Pseudoscalar_mH-400_ma-200": merged_dataset(pattern="mH-400_ma-200"),
        "Pseudoscalar_mH-400_ma-300": merged_dataset(pattern="mH-400_ma-300"),
        "Pseudoscalar_mH-500_ma-100": merged_dataset(pattern="mH-500_ma-100"),
        "Pseudoscalar_mH-500_ma-200": merged_dataset(pattern="mH-500_ma-200"),
        "Pseudoscalar_mH-500_ma-300": merged_dataset(pattern="mH-500_ma-300"),
        "Pseudoscalar_mH-500_ma-400": merged_dataset(pattern="mH-500_ma-400"),
        "Pseudoscalar_mH-600_ma-100": merged_dataset(pattern="mH-600_ma-100"),
        "Pseudoscalar_mH-600_ma-200": merged_dataset(pattern="mH-600_ma-200"),
        "Pseudoscalar_mH-600_ma-300": merged_dataset(pattern="mH-600_ma-300"),
        "Pseudoscalar_mH-600_ma-400": merged_dataset(pattern="mH-600_ma-400"),
        "Pseudoscalar_mH-600_ma-500": merged_dataset(pattern="mH-600_ma-500"),
        "Pseudoscalar_mH-700_ma-100": merged_dataset(pattern="mH-700_ma-100"),
        "Pseudoscalar_mH-700_ma-200": merged_dataset(pattern="mH-700_ma-200"),
        "Pseudoscalar_mH-700_ma-300": merged_dataset(pattern="mH-700_ma-300"),
        "Pseudoscalar_mH-700_ma-400": merged_dataset(pattern="mH-700_ma-400"),
        "Pseudoscalar_mH-700_ma-500": merged_dataset(pattern="mH-700_ma-500"),
        "Pseudoscalar_mH-800_ma-100": merged_dataset(pattern="mH-800_ma-100"),
        "Pseudoscalar_mH-800_ma-200": merged_dataset(pattern="mH-800_ma-200"),
        "Pseudoscalar_mH-800_ma-300": merged_dataset(pattern="mH-800_ma-300"),
        "Pseudoscalar_mH-800_ma-400": merged_dataset(pattern="mH-800_ma-400"),
        "Pseudoscalar_mH-800_ma-500": merged_dataset(pattern="mH-800_ma-500"),
        "Pseudoscalar_mH-900_ma-100": merged_dataset(pattern="mH-900_ma-100"),
        "Pseudoscalar_mH-900_ma-200": merged_dataset(pattern="mH-900_ma-200"),
        "Pseudoscalar_mH-900_ma-300": merged_dataset(pattern="mH-900_ma-300"),
        "Pseudoscalar_mH-900_ma-400": merged_dataset(pattern="mH-900_ma-400"),
        "Pseudoscalar_mH-900_ma-500": merged_dataset(pattern="mH-900_ma-500"),
    }


if __name__ == '__main__':
    locate_root_files()
