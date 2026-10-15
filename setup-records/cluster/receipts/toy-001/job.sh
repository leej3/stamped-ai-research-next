#!/bin/bash
#SBATCH --account=pi_d31548v_dartmouth_edu
#SBATCH --partition=cpu
#SBATCH --time=00:05:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --job-name=stamped-toy
#SBATCH --output=experiments/cluster/scheduler/%j.out
#SBATCH --error=experiments/cluster/scheduler/%j.err
set -euo pipefail
cd /work/pi_d31548v_dartmouth_edu/stamped-ai-research-next/setup-probe/toy-001
/home/f008q9c_dartmouth_edu/.pixi/bin/pixi run --locked --manifest-path /work/pi_d31548v_dartmouth_edu/stamped-ai-research-next/setup-probe/toy-001/pixi.toml duct -p experiments/cluster/logs/toy-001/run_ --fail-time 0 --capture-outputs all --outputs all --record-types all python experiments/datalad-annex/compute.py
