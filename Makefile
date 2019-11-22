PREFIX = build
CMSSW_VER = CMSSW_10_6_4
PYTHON = PYTHONPATH=$(shell pwd):$$PYTHONPATH /usr/bin/env python3 -u
include $(PREFIX)/.cmsenv
MonoZ = $(CMSSW_BASE)/src/MonoZ
NanoAODTools = $(CMSSW_BASE)/src/NanoAODTools
coffea = $(CMSSW_BASE)/src/coffea

voms = /tmp/x509up_u$(UID)

.PHONY: help clean $(coffea) WS_proc 2hdm

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

$(PREFIX)/.cmsenv:
	mkdir -p $(PREFIX)
	cd $(PREFIX) && scramv1 project CMSSW $(CMSSW_VER)
	cd $(PREFIX)/$(CMSSW_VER) && scramv1 runtime -sh | tr -d '";' > ../.cmsenv

$(MonoZ):
	git clone git@github.com:yhaddad/MonoZNanoAOD.git $(MonoZ)

$(NanoAODTools):
	git clone git@github.com:yhaddad/nanoAOD-tools.git $(NanoAODTools)
	cd $(NanoAODTools) && git checkout remotes/origin/topic-Run2-Lepton-SF && scram b -j 10

$(coffea):
	git clone git@github.com:coffeateam/coffea.git $(coffea) || cd $(coffea) && git reset --hard && git pull
	cp -r override/coffea $(coffea)
	cd $(coffea) && $(PYTHON) $(coffea)/setup.py install --user

$(CMSSW_BASE)/%: $(basename %) $(MonoZ)
	install -D $< $@

$(MonoZ)/condor/condor_run_WS_proc: $(coffea) $(MonoZ)/python/producers.py $(MonoZ)/condor/data.txt

WS_proc: $(voms) $(MonoZ)/condor/condor_run_WS_proc
	cd $(PREFIX) && $(PYTHON) $(MonoZ)/condor/condor_run_WS_proc \
	--era=2018 \
	--isMC=1 \
	--tag=Exorcism2018 \
	--input=data.txt \
	--force \
	| tee output.log

2hdm: $(coffea)
	cd $(PREFIX) && $(PYTHON) -m 2hdm_explorer
