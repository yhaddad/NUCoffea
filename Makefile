PREFIX = $(shell pwd)/build

CMSSW_VER = CMSSW_10_6_4

COFFEA_VER = 0.6.19
FROZEN_COFFEA_DEPS = \
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

voms = /tmp/x509up_u$(UID)
cmsenv = $(PREFIX)/.cmsenv
venv = $(PREFIX)/.venv
include $(cmsenv)
MonoZ = $(CMSSW_BASE)/src/MonoZ
NanoAODTools = $(CMSSW_BASE)/src/NanoAODTools
coffea = $(CMSSW_BASE)/src/coffea
coffea_lock = $(coffea)/lock
coffea_overrides = $(coffea)/coffea/processor/processor.py $(coffea)/coffea/processor/executor.py

PYTHON_ENV = PYTHONPATH=$(shell pwd):$$PYTHONPATH PYTHONUNBUFFERED=1
BASE_PYTHON = /bin/env python3

PYTHON = $(PYTHON_ENV) $(venv)/bin/python

.PHONY: help clean WS_proc 2hdm get-upstream

help:
	@echo "available targets:"
	@echo "  WS_proc                        submit WS_proc to condor."
	@echo "  2hdm                           run 2hdm explorer."
	@echo "  clean                          clean up '$(PREFIX)'."
	@echo "  get-upstream [branch=master]   incorporate force pushed changes"
	@echo "  help                           show this message."

clean:
	rm -rf $(PREFIX)

$(voms):
	voms-proxy-init --voms cms

$(cmsenv):
	mkdir -p $(PREFIX)
	cd $(PREFIX) && scramv1 project CMSSW $(CMSSW_VER)
	cd $(PREFIX)/$(CMSSW_VER) && scramv1 runtime -sh | tr -d '";' > ../.cmsenv

$(venv):
	$(PYTHON_ENV) $(BASE_PYTHON) -m venv $(venv) --system-site-packages

$(MonoZ):
	git clone git@github.com:yhaddad/MonoZNanoAOD.git $(MonoZ)

$(NanoAODTools):
	git clone git@github.com:yhaddad/nanoAOD-tools.git $(NanoAODTools)
	cd $(NanoAODTools) && git checkout remotes/origin/topic-Run2-Lepton-SF && scram b -j 10

$(coffea)/dl: $(venv)
	git clone git@github.com:coffeateam/coffea.git $(coffea) || true
	cd $(coffea) && git fetch && git checkout tags/v$(COFFEA_VER) && git reset --hard && \
	rm $(coffea_overrides) && touch dl

$(coffea)/%: override/% $(coffea)/dl
	install -D $< $@

$(coffea_lock): $(coffea_overrides)
	$(PYTHON) -m pip install $(FROZEN_COFFEA_DEPS)
	cd $(coffea) && $(PYTHON) setup.py install
	$(PYTHON) -m pip freeze | grep coffea && touch $(coffea_lock)

$(CMSSW_BASE)/%: $(basename %) $(MonoZ)
	install -D $< $@

$(MonoZ)/condor/condor_run_WS_proc: $(coffea_lock) $(MonoZ)/python/producers.py $(MonoZ)/condor/data.txt

WS_proc: $(voms) $(MonoZ)/condor/condor_run_WS_proc
	cd $(PREFIX) && $(PYTHON) $(MonoZ)/condor/condor_run_WS_proc \
	--era=2018 \
	--isMC=1 \
	--tag=Exorcism2018 \
	--input=data.txt \
	--force \
	| tee $@.log

2hdm: $(coffea_lock)
	cd $(PREFIX) && $(PYTHON) -m 2hdm_explorer \
	| tee $@.log

branch = $(or $(branch), master)
get-upstream:
	git fetch && \
	git stash && \
	git checkout origin/$(branch) && \
	git branch -D $(branch) && \
	git checkout $(branch) && \
	git stash pop
