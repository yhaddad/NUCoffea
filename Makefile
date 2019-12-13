# useful targets:
#   quick_WS                       quick submit WS_proc to condor.
#   condor_run_WS_proc             run condor_run_WS_proc.
#   condor_submit                  submit a recipe to run on condor.
#   2hdm                           run 2hdm explorer.
#   WS_proc                        run the WS proc.
#   get-upstream [branch=master]   incorporate force pushed changes.
#   clean                          clean up build/.
#   help                           show this message.
#
# arguments:
#   branch=master                  branch to use for get-upstream.
#   override_coffea=yes            use coffea file replacements in override/.
#                                    'yes': patch coffea library.
#                                    'no': use official coffea library.
#   coffeadeps=freeze              how to handle dependencies of coffea.
#                                   'freeze': use frozen coffea deps.
#                                   'lcg': use LCG98 environment.
#   condor_submit arguments:
#     proc=help                    make(1) recipe to run on condor.
#                                    '2hdm': submit 2hdm.
#                                    'WS_proc': submit WS_proc.
#     use_docker=                  define this to use docker.
#     queue=testmatch              queueing style.
#     era                          era. Forwarded to the job recipe.
#     isMC                         isMC. Forwarded to the job recipe.
#     tag                          tag.
#     sample                       data/MC sample.
#   WS_proc arguments:
#     era                          era.
#     isMC                         isMC.
#     jobNum                       jobNum.
#     infile                       infile.
#
# TODO test LCG deps
# TODO only use venv tar for docker
# TODO test docker
# TODO optimize make recipe caching
# FIXME N.B. (for now): run make $(pwd)/venv.tar.gz before doing quick_WS !!

.PHONY: help clean WS_proc 2hdm get-upstream condor_submit quick_WS condor_run_WS_proc


#### Static Variables of Interest ####

WORK_DIR := $(shell pwd)/build

CMSSW_VER := CMSSW_10_6_4

COFFEA_VER := 0.6.19

FROZEN_COFFEA_DEPS := \
awkward==0.12.17 \
backports.lzma==0.0.14 \
cachetools==3.1.1 \
certifi==2019.9.11 \
cloudpickle==1.2.2 \
cycler==0.10.0 \
kiwisolver==1.1.0 \
llvmlite==0.30.0 \
lz4==2.2.1 \
matplotlib==3.1.2 \
mplhep==0.0.17 \
numba==0.46.0 \
numpy==1.17.4 \
pyparsing==2.4.5 \
python-dateutil==2.8.1 \
requests==2.22.0 \
scipy==1.3.3 \
tqdm==4.39.0 \
uproot==3.10.12 \
uproot-methods==0.7.1 \
urllib3==1.25.7

BASE_PYTHON := /bin/env python3
PYTHON_ENV := PYTHONPATH=$(shell pwd):$$PYTHONPATH PYTHONUNBUFFERED=1


#### General Commands ####

help:
	@while read line; do [[ "$$line" =~ \# ]] && echo "$$line" | tr -d \# | cut -d \  -f2- || break; done < Makefile

clean:
	rm -rf $(WORK_DIR)

VOMS := /tmp/x509up_u$(UID)
$(VOMS):
	grid-proxy-info || voms-proxy-init --voms cms

$(WORK_DIR):
	mkdir -p $(WORK_DIR)

branch := $(or $(branch), master)
get-upstream:
	git fetch && \
	git stash && \
	git checkout origin/$(branch) && \
	git branch -D $(branch) && \
	git checkout $(branch) && \
	git stash pop


#### NanoAODTools Recipies ####

CMSENV := $(WORK_DIR)/.cmsenv
$(CMSENV):
	mkdir -p $(WORK_DIR)
	cd $(WORK_DIR) && scramv1 project CMSSW $(CMSSW_VER)
	cd $(WORK_DIR)/$(CMSSW_VER) && scramv1 runtime -sh > $@

NANOAOD := $(WORK_DIR)/$(CMSSW_VER)/src/NanoAODTools
$(NANOAOD): $(CMSENV)
	git clone git@github.com:yhaddad/nanoAOD-tools.git $@
	cd $@ && git checkout remotes/origin/topic-Run2-Lepton-SF && scram b -j 10

MONOZ := $(WORK_DIR)/$(CMSSW_VER)/src/MonoZ
$(MONOZ): $(NANOAOD)
	git clone git@github.com:yhaddad/MonoZNanoAOD.git $@


#### Coffea Recipies ####

coffea := $(WORK_DIR)/coffea-src
override_coffea := $(or $(override_coffea), yes)
COFFEA_OVERRIDES := $(shell cd override/ && find coffea -type f -exec echo -n $(coffea)/{}\  \;)

$(coffea)/dl:
	git clone git@github.com:coffeateam/coffea.git $(coffea) || true
	cd $(coffea) && git fetch && git checkout tags/v$(COFFEA_VER) && git reset --hard
ifeq ($(override_coffea), yes)
	rm $(COFFEA_OVERRIDES)
endif
	touch dl

$(coffea)/%: override/% $(coffea)/dl
ifeq ($(override_coffea), yes)
	install -D $< $@
endif

coffeadeps := $(or $(coffeadeps), freeze)
LCG := /cvmfs/sft.cern.ch/lcg/views/LCG_96python3/x86_64-centos7-gcc8-opt/setup.sh

VENV_TAR := $(shell pwd)/venv.tar.gz
$(VENV_TAR): $(COFFEA_OVERRIDES)
	$(PYTHON_ENV) $(BASE_PYTHON) -m venv $(VENV).tmp --copies
ifeq ($(coffeadeps), freeze)
	$(PYTHON_ENV) $(VENV).tmp/bin/python -m pip install $(FROZEN_COFFEA_DEPS)
	cd $(coffea) && $(PYTHON_ENV) $(VENV).tmp/bin/python setup.py install
endif
ifeq ($(coffeadeps), lcg)
	source $LCG && cd $(coffea) && $(PYTHON_ENV) $(VENV).tmp/bin/python setup.py install
endif
	cd  $(VENV).tmp && tar czf $(VENV_TAR) .

VENV := $(WORK_DIR)/venv
$(VENV):
	mkdir -p $(VENV)
	tar xzf $(VENV_TAR) -C $(VENV)


#### Proc Runners ####

WS_proc: $(VENV)
	@test -n '$(jobNum)' && test -n '$(isMC)' && test -n '$(era)' && test -n '$(infile)'
	time $(PYTHON_ENV) $(VENV)/bin/python condor_WS_proc.py \
	--jobNum $(jobNum) \
	--isMC $(isMC) \
	--era $(era) \
	--infile $(infile)

2hdm: $(VENV)
	cd $(WORK_DIR) && time $(PYTHON_ENV) $(VENV)/bin/python -m 2hdm_explorer \
	| tee $@.log


#### Condor Submission ####

proc := $(or $(proc), help)
queue := $(or $(queue), testmatch)
JOB_DIR := $(WORK_DIR)/jobs_$(tag)_$(sample)
INPUT_DIR := /eos/cms/store/group/phys_exotica/monoZ/$(tag)/$(sample)
OUTPUT_DIR := /eos/user/j/jabernha/monoZ/$(tag)/$(sample)

ifdef use_docker
define CONDOR_DOCKER_PARAMS
universe                = docker
docker_image            = debian
request_memory          = 100M
endef
endif

define CONDOR_PARAMS
$(CONDOR_DOCKER_PARAMS)
executable              = $(shell which $(MAKE))
arguments               = $(proc) jobNum=$$(ProcId) infile=$$(jobid) isMC=$(isMC) era=$(era)
should_transfer_files   = YES
when_to_transfer_output = ON_EXIT
transfer_input_files    = $(shell ls -1I $(shell basename $(WORK_DIR)) | while read line; do echo -n $$(pwd)/$$line,; done)
output                  = $(JOB_DIR)/$$(ClusterId).$$(ProcId).out
error                   = $(JOB_DIR)/$$(ClusterId).$$(ProcId).err
log                     = $(JOB_DIR)/$$(ClusterId).$$(ProcId).log
request_disk            = 1000000
queue jobid from $(JOB_DIR)/inputfiles.dat
+JobFlavour             = "$(queue)"
endef
export CONDOR_PARAMS

$(JOB_DIR):
	rm -rf $(JOB_DIR)
	mkdir -p $(JOB_DIR)

$(JOB_DIR)/inputfiles.dat:
	ls -1d $(INPUT_DIR)/* > $@

$(JOB_DIR)/%.sub: $(JOB_DIR) $(JOB_DIR)/inputfiles.dat
	echo "$$CONDOR_PARAMS" | tee $@

JOB_SUB := $(JOB_DIR)/$(tag)_$(sample).sub
condor_submit: $(VOMS) $(JOB_SUB)
	mkdir -p $(OUTPUT_DIR)
	cd $(OUTPUT_DIR) && condor_submit $(JOB_SUB)


#### Handy Aliases ####

quick_WS:
	rm -f $(WORK_DIR)/$@.log
	while read line; do \
	$(MAKE) condor_submit \
	proc=WS_proc \
	era=2018 \
	isMC=1 \
	tag=Exorcism2018 \
	sample=$$(echo $$line | cut -d \/ -f2) | tee -a $(WORK_DIR)/$@.log; \
	done \
	< data.txt


#### condor_run2_proc-style Submitters ####

condor_run_WS_proc: $(VOMS) $(VENV) condor_run_WS_proc.py
	cd $(WORK_DIR) && $(PYTHON_ENV) CMSSW_BASE=$(WORK_DIR) $(BASE_PYTHON) ../condor_run_WS_proc.py \
	--era=2018 \
	--isMC=1 \
	--tag=Exorcism2018 \
	--input=../data.txt \
	--force \
	| tee $@.log

