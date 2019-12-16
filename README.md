# MonoZCoffea
MonoZ analysis using [Coffea](https://coffeateam.github.io/coffea/)

## Quick start

### 2HDM+a Explorer
- run `python3 -m 2hdm_explorer` with pyYAML and Coffea installed
- can do this by running `make 2hdm`

### MonoZ Workspace Producer
1. In the Makefile, change where it says OUTPUT_DIR to wherever you have write access

2. `make $(pwd)/venv.tar.gz`<sup>1</sup>

3. `make quick_WS`

-- or --

1. `make condor_run_WS_proc`


### Notes

#### environment / "proc scripts"
I use make so that I can provision the environment _as needed_<sup>1</sup> (adds ease for newcomers) and to have more flexibility wrangling config files with shell.

<sup>1</sup>One of the benefits of using make is that it caches intermediate products so when you run the same recipe it is much faster the second time. I haven't quite figured out all of the criteria it uses to determine whether some output is "up to date", so the caching behavior here isn't ideal yet. In light of this, I've temporarily removed `$(VENV_TAR)` as a dep for `quick_WS`.

There are still a couple of environmental things that need to be debugged. I'm tarring and uploading the python environment to condor jobs, like in https://coffeateam.github.io/coffea/installation.html#install-via-cvmfs, but this may not be necessary for non-docker jobs. Also, docker jobs need to be tested, as well as the cvmfs coffea dependency resolution (same link above) which seems attractive because it's fast and lightweight.

The main issue with docker is that /eos is not mounted in job containers. This is needed to read the MC dataset or kinematic trees off of eos, but docker mounts are set by the HTCondor admins in the condor_config files. Saving and running are already set up here to work without /eos or /afs mounted, via file transfer. I'm thinking the input may be very large, so it isn't worth using the file transfer feature to send the input to the jobs.

#### coffea
With the exception of a few bugs in coffea and uproot, the workspace producer seemed to port well to coffea, and it runs very fast (~1 min). The complicated logic in the kinematics producer will require some thought though.

## Requirements

- Python 3
- HTCondor cluster

