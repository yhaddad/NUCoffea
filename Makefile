PREFIX = build
CMSSW_VER = CMSSW_10_6_4
COFFEA_VER = 0.6.19
cmsenv = $(PREFIX)/.cmsenv
include $(cmsenv)
MonoZ = $(CMSSW_BASE)/src/MonoZ
NanoAODTools = $(CMSSW_BASE)/src/NanoAODTools
coffea = $(CMSSW_BASE)/src/coffea
coffea_lock = $(coffea)/lock
coffea_overrides = $(coffea)/coffea/processor/processor.py $(coffea)/coffea/processor/executor.py

PYTHON = PYTHONPATH=$(shell pwd):$$PYTHONPATH /usr/bin/env python3 -u

voms = /tmp/x509up_u$(UID)

.PHONY: help clean WS_proc 2hdm

help:
	@echo "available targets:"
	@echo "  WS_proc    submit WS_proc to condor."
	@echo "  2hdm       run 2hdm explorer."
	@echo "  clean      clean up '$(PREFIX)'."
	@echo "  help       show this message."

clean:
	rm -rf $(PREFIX)

$(voms):
	voms-proxy-init --voms cms

$(cmsenv):
	mkdir -p $(PREFIX)
	cd $(PREFIX) && scramv1 project CMSSW $(CMSSW_VER)
	cd $(PREFIX)/$(CMSSW_VER) && scramv1 runtime -sh | tr -d '";' > ../.cmsenv

$(MonoZ):
	git clone git@github.com:yhaddad/MonoZNanoAOD.git $(MonoZ)

$(NanoAODTools):
	git clone git@github.com:yhaddad/nanoAOD-tools.git $(NanoAODTools)
	cd $(NanoAODTools) && git checkout remotes/origin/topic-Run2-Lepton-SF && scram b -j 10

$(coffea):
	git clone git@github.com:coffeateam/coffea.git $(coffea) || true
	cd $(coffea) && git fetch && git checkout tags/v$(COFFEA_VER) && git reset --hard
	touch -d0 $(coffea_overrides)

$(coffea)/%: override/% $(coffea)
	install -D $< $@

$(coffea_lock): $(coffea_overrides)
	# FIXME to venv
	$(PYTHON) -m pip install --user \
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
	cd $(coffea) && $(PYTHON) setup.py install --user
	$(PYTHON) -m pip freeze --user | grep coffea && touch $(coffea_lock)

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
	| tee output.log

2hdm: $(coffea_lock)
	cd $(PREFIX) && $(PYTHON) -m 2hdm_explorer
