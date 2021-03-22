import os, sys
import argparse
import logging
import pwd
import subprocess
import shutil
import time
from termcolor import colored

logging.basicConfig(level=logging.DEBUG)

script_TEMPLATE = """#!/bin/bash

source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc6_amd64_gcc630

cd {cmssw_base}/src/
eval `scramv1 runtime -sh`
echo
echo $_CONDOR_SCRATCH_DIR
cd   $_CONDOR_SCRATCH_DIR
echo
echo "... start job at" `date "+%Y-%m-%d %H:%M:%S"`
echo "----- directory before running:"
ls -lR .
echo "----- CMSSW BASE, python path, pwd:"
echo "+ CMSSW_BASE  = $CMSSW_BASE"
echo "+ PYTHON_PATH = $PYTHON_PATH"
echo "+ PWD         = $PWD"
xrdcp {file_full_name} .
python condor_coffea_WS.py --jobNum=$1 --isMC={ismc} --era={era} --infile={file_name}
rm {file_name}
echo "----- transfer output to eos :"
xrdcp -s -f tree_$1.root {eosdir}
echo "----- directory after running :"
ls -lR .
echo " ------ THE END (everyone dies !) ----- "
"""


condor_TEMPLATE = """
request_disk          = 1000000
executable            = {jobdir}/script.sh
arguments             = $(ProcId) $(jobid)
transfer_input_files  = {transfer_file}
output                = $(ClusterId).$(ProcId).out
error                 = $(ClusterId).$(ProcId).err
log                   = $(ClusterId).$(ProcId).log
initialdir            = {jobdir}
transfer_output_files = ""
+JobFlavour           = "{queue}"

queue jobid from {jobdir}/inputfiles.dat
"""

def main():
    parser = argparse.ArgumentParser(description='Famous Submitter')
    parser.add_argument("-i"   , "--input" , type=str, default="data.txt" , help="input datasets", required=True)
    parser.add_argument("-t"   , "--tag"   , type=str, default="Exorcism"  , help="production tag", required=True)
    parser.add_argument("-isMC", "--isMC"  , type=int, default=1          , help="")
    parser.add_argument("-q"   , "--queue" , type=str, default="testmatch", help="")
    parser.add_argument("-e"   , "--era"   , type=str, default="2017"     , help="")
    parser.add_argument("-f"   , "--force" , action="store_true"          , help="recreate files and jobs")
    parser.add_argument("-s"   , "--submit", action="store_true"          , help="submit only")
    parser.add_argument("-dry" , "--dryrun", action="store_true"          , help="running without submission")

    options = parser.parse_args()

    # Making sure that the proxy is good
    cmssw_base = os.environ['CMSSW_BASE']
    eosbase = "/eos/cms/store/group/phys_exotica/monoZ/{tag}/{sample_dataset}/"
    group_base = "group/phys_exotica"
    my_base = "user/cfreer"

    with open(options.input, 'r') as stream:
        for sample in stream.read().split('\n'):
            if '#' in sample: continue
            if len(sample.split('/')) <= 1: continue
            dataset = sample.split("/")[9]#this is the dataset
            name_of_file = sample.split("/")[10]#this is the filename
            jobs_dir = '_'.join(['jobs', options.tag, dataset, name_of_file])
            logging.info("-- sample_name : " + sample)

            if os.path.isdir(jobs_dir):
                if not options.force:
                    logging.error(" " + jobs_dir + " already exist !")
                    continue
                else:
                    logging.warning(" " + jobs_dir + " already exists, forcing its deletion!")
                    shutil.rmtree(jobs_dir)
                    os.mkdir(jobs_dir)
            else:
                os.mkdir(jobs_dir)

            eosindir = eosbase.format(tag=options.tag,sample_dataset=dataset)
            time.sleep(1)
            #eosoutdir = eosbase.format(tag=options.tag,sample=sample_name).replace(group_base,my_base)
            eosoutdir = eosbase.format(tag=options.tag+"_WS",sample_dataset=dataset)
            # crete a directory on eos
            if '/eos/cms' in eosoutdir:
                eosoutdir = eosoutdir.replace('/eos/cms', 'root://eoscms.cern.ch/')
                os.system("eos mkdir -p {}".format(eosoutdir.replace('root://eoscms.cern.ch/','')))
            else:
                raise NameError(eosoutdir)

            with open(os.path.join(jobs_dir, "script.sh"), "w") as scriptfile:
                script = script_TEMPLATE.format(
                    cmssw_base=cmssw_base,
                    ismc=options.isMC,
                    era=options.era,
                    eosdir=eosoutdir,
                    file_full_name = sample,
                    file_name = name_of_file
                )
                scriptfile.write(script)
                scriptfile.close()

            with open(os.path.join(jobs_dir, "condor.sub"), "w") as condorfile:
                condor = condor_TEMPLATE.format(
                    transfer_file= ",".join([
                        "../condor_SUEPProducer.py",
                    ]),
                    jobdir=jobs_dir,
                    queue=options.queue
                )
                condorfile.write(condor)
                condorfile.close()
            if options.dryrun:
                continue

            htc = subprocess.Popen(
                "condor_submit " + os.path.join(jobs_dir, "condor.sub"),
                shell  = True,
                stdin  = subprocess.PIPE,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
                close_fds=True
            )
            out, err = htc.communicate()
            exit_status = htc.returncode
            logging.info("condor submission status : {}".format(exit_status))

if __name__ == "__main__":
    main()

