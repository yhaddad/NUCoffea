import os
import re

from coffea.processor import run_uproot_job, futures_executor

from WSProducer import MonoZ

import uproot
import argparse

parser = argparse.ArgumentParser("")
parser.add_argument('--isMC', type=int, default=1, help="")
parser.add_argument('--jobNum', type=int, default=1, help="")
parser.add_argument('--era', type=str, default="2018", help="")
parser.add_argument('--doSyst', type=int, default=1, help="")
parser.add_argument('--infile', type=str, default=None, help="")
parser.add_argument('--dataset', type=str, default="X", help="")
parser.add_argument('--nevt', type=str, default=-1, help="")

options = parser.parse_args()


def inputfile(nanofile):
    tested = False
    forceaaa = False
    pfn = os.popen("edmFileUtil -d %s" % (nanofile)).read()
    pfn = re.sub("\n", "", pfn)
    print((nanofile, " -> ", pfn))
    if (os.getenv("GLIDECLIENT_Group", "") != "overflow" and
            os.getenv("GLIDECLIENT_Group", "") != "overflow_conservative" and not
            forceaaa):
        if not tested:
            print("Testing file open")
            testfile = uproot.open(pfn)
            if testfile:
                print("Test OK")
                nanofile = pfn
            else:
                if "root://cms-xrd-global.cern.ch/" not in nanofile:
                    nanofile = "root://cms-xrd-global.cern.ch/" + nanofile
                forceaaa = True
        else:
            nanofile = pfn
    else:
        if "root://cms-xrd-global.cern.ch/" not in nanofile:
            nanofile = "root://cms-xrd-global.cern.ch/" + nanofile
    return nanofile


# options.infile = inputfile(options.infile)
# edmFileUtil in CMSSW...

print(f"""
---------------------------
 -- options  = {options}
 -- is MC    = {options.isMC}
 -- jobNum   = {options.jobNum}
 -- era      = {options.era}
 -- in file  = {options.infile}
 -- dataset  = {options.dataset}
---------------------------
""")

if options.isMC:
    condtag_ = "NANOAODSIM"
    if options.dataset == "X":
        options.dataset = options.infile
        options.dataset = options.dataset.split('/store')[1].split("/")
        condtag_ = options.dataset[5]
        options.dataset = options.dataset[3]
    print(("[check] condtag_ == ", condtag_))
    print(("[check] dataset  == ", options.dataset))
else:
    if options.dataset == "X":
        options.dataset = options.infile
        options.dataset = options.dataset.split('/store')[1].split("/")
        condtag_ = options.dataset[2]
        options.dataset = options.dataset[3]
    else:
        options.dataset = options.dataset.split("/")
        condtag_ = options.dataset[2]
        options.dataset = options.dataset[1]

pre_selection = ""

if float(options.nevt) > 0:
    print((" passing this cut and : ", options.nevt))
    pre_selection += ' && (Entry$ < {})'.format(options.nevt)

pro_syst = ["ElectronEn", "MuonEn", "jesTotal", "jer"]
ext_syst = ["puWeight", "PDF", "MuonSF", "ElecronSF", "EWK", "nvtxWeight", "TriggerSFWeight", "btagEventWeight",
            "QCDScale0w", "QCDScale1w", "QCDScale2w"]

modules_era = []

modules_era.append(MonoZ(isMC=options.isMC, era=int(options.era), do_syst=1, syst_var='', sample=options.dataset,
                         haddFileName="tree_%s.root" % str(options.jobNum)))

for sys in pro_syst:
    for var in ["Up", "Down"]:
        # modules_era.append(MonoZProducer(options.isMC, str(options.era), do_syst=1, syst_var=sys+var))
        modules_era.append(MonoZ(options.isMC, str(options.era), do_syst=1,
                                 syst_var=sys + var, sample=options.dataset,
                                 haddFileName="tree_%s.root" % str(options.jobNum)))

for sys in ext_syst:
    for var in ["Up", "Down"]:
        modules_era.append(
            MonoZ(
                options.isMC, str(options.era),
                do_syst=1, syst_var=sys + var,
                weight_syst=True,
                sample=options.dataset,
                haddFileName="tree_%s.root" % str(options.jobNum),
            )
        )

# aif options.isMC:
#   modules_era.append(VBSProducer(isMC=options.isMC, era=str(options.era), do_syst=1, syst_var=''))
# else:
#   print "sample : ", options.dataset, " candtag : ", condtag_
#   modules_era.append(VBSProducer(isMC=options.isMC, era=str(options.era), do_syst=1, syst_var=''))

for i in modules_era:
    print("modules : ", i)

print("Selection : ", pre_selection)

# p = PostProcessor(
#    ".", [options.infile],
#    cut=pre_selection,
#    #branchsel="keep_and_drop_VBS.txt",
#    outputbranchsel="keep_and_drop_WS.txt",
#    haddFileName="tree_%s.root" % str(options.jobNum),
#    modules=modules_era,
#    provenance=True,
#    noOut=False,
#    fwkJobReport=True,
#    jsonInput=None
# )
# p.run()
for instance in modules_era:
    run_uproot_job(
        {instance.sample: [options.infile]},
        treename='Events',
        processor_instance=instance,
        executor=futures_executor,
        executor_args={'workers': 10},
        chunksize=500000
    )
