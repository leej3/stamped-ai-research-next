#!/usr/bin/env python3
"""Transfer the recorded toy environment, run one Slurm job and retrieve evidence."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/datalad-annex"))
from trial import verify


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--host", default="unity")
    parser.add_argument("--remote-base", default="/work/pi_d31548v_dartmouth_edu/stamped-ai-research-next/setup-probe")
    parser.add_argument("--pixi", default="/home/f008q9c_dartmouth_edu/.pixi/bin/pixi")
    parser.add_argument("--account", default="pi_d31548v_dartmouth_edu")
    parser.add_argument("--partition", default="cpu")
    args = parser.parse_args()
    if not args.run_id.replace("-", "").isalnum():
        parser.error("Run ID must contain only letters, digits and hyphens")
    receipts = HERE / "receipts" / args.run_id
    receipts.mkdir(parents=True, exist_ok=False)
    remote = f"{args.remote_base}/{args.run_id}"
    commands = []

    def command(argv, timeout=180):
        argv = list(map(str, argv))
        number = len(commands) + 1
        print(f"COMMAND {number}: {shlex.join(argv)}", flush=True)
        record = dict(argv=argv, number=number, started_unix=time.time())
        stdout, stderr = b"", b""
        try:
            result = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=timeout)
            stdout, stderr = result.stdout, result.stderr
            record.update(returncode=result.returncode, outcome="exited")
        except subprocess.TimeoutExpired as error:
            stdout, stderr = error.stdout or b"", error.stderr or b""
            record.update(returncode=None, outcome="timeout", error=str(error))
        except OSError as error:
            record.update(returncode=None, outcome="spawn_error", error=str(error))
        record["elapsed_seconds"] = time.time() - record["started_unix"]
        (receipts / f"{number:03d}.stdout").write_bytes(stdout)
        (receipts / f"{number:03d}.stderr").write_bytes(stderr)
        commands.append(record)
        save(receipts / "commands.json", commands)
        print(stdout.decode(errors="replace"), end="", flush=True)
        print(stderr.decode(errors="replace"), end="", file=sys.stderr, flush=True)
        if record["returncode"] != 0:
            raise RuntimeError(f"Command {number} failed; preserved {record['outcome']}")
        return stdout.decode().strip()

    def ssh(script, timeout=180):
        return command(["ssh", "-o", "BatchMode=yes", args.host, script], timeout)

    def copy(source, destination):
        return command(["scp", "-r", "-o", "BatchMode=yes", source, destination])

    sources = ["pixi.toml", "pixi.lock", "experiments/datalad-annex/compute.py",
               "experiments/datalad-annex/input.csv"]
    hashes = {name: sha(args.source / name) for name in sources}
    if any(sha(ROOT / name) != digest for name, digest in hashes.items()):
        raise RuntimeError("Source and installed local task bytes differ")
    save(receipts / "sources.json", dict(source=str(args.source), hashes=hashes,
         remote=remote, host=args.host, python=sys.executable,
         task_commit=command(["git", "rev-parse", "HEAD"])))
    summary = dict(status="running", run_id=args.run_id, remote=remote, hashes=hashes)
    try:
        ssh("set -eu; " + shlex.join(["mkdir", remote]) + "; " + shlex.join([
            "mkdir", "-p", remote + "/experiments/datalad-annex",
            remote + "/experiments/cluster/scheduler"]))
        copy(args.source / "pixi.toml", f"{args.host}:{remote}/pixi.toml")
        copy(args.source / "pixi.lock", f"{args.host}:{remote}/pixi.lock")
        for name in sources[2:]:
            copy(args.source / name, f"{args.host}:{remote}/{name}")
        remote_hashes = ssh(f"cd {shlex.quote(remote)} && " + shlex.join(["sha256sum", *sources]))
        observed_hashes = {line.split(None, 1)[1].strip(): line.split()[0]
                           for line in remote_hashes.splitlines()}
        if observed_hashes != hashes:
            raise RuntimeError("Transfer hashes differ")
        save(receipts / "transferred-hashes.json", observed_hashes)
        ssh(shlex.join([args.pixi, "--version"]))
        ssh(shlex.join([args.pixi, "install", "--locked", "--manifest-path", remote + "/pixi.toml"]), timeout=900)
        script = "\n".join([
            "#!/bin/bash", f"#SBATCH --account={args.account}",
            f"#SBATCH --partition={args.partition}", "#SBATCH --time=00:05:00",
            "#SBATCH --cpus-per-task=1", "#SBATCH --mem=2G",
            "#SBATCH --job-name=stamped-toy", "#SBATCH --output=experiments/cluster/scheduler/%j.out",
            "#SBATCH --error=experiments/cluster/scheduler/%j.err", "set -euo pipefail",
            "cd " + shlex.quote(remote),
            shlex.join([args.pixi, "run", "--locked", "--manifest-path", remote + "/pixi.toml",
                        "duct", "-p", f"experiments/cluster/logs/{args.run_id}/run_",
                        "--fail-time", "0", "--capture-outputs", "all", "--outputs", "all",
                        "--record-types", "all", "python", "experiments/datalad-annex/compute.py"]), ""])
        (receipts / "job.sh").write_text(script)
        copy(receipts / "job.sh", f"{args.host}:{remote}/experiments/cluster/job.sh")
        job = ssh(f"cd {shlex.quote(remote)} && sbatch --parsable experiments/cluster/job.sh").split(";")[0]
        if not job.isdigit():
            raise RuntimeError("Unexpected sbatch job ID")
        summary["job_id"] = job
        save(receipts / "submitted.json", summary)
        deadline = time.monotonic() + 900
        terminal = {"COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "OUT_OF_MEMORY", "NODE_FAIL", "PREEMPTED"}
        while True:
            accounting = ssh(shlex.join(["sacct", "-j", job, "--noheader", "--parsable2", "--format",
                                        "JobIDRaw,State,ExitCode,Elapsed,AllocCPUS,MaxRSS,ReqMem,NodeList"]))
            (receipts / "sacct.txt").write_text(accounting + "\n")
            rows = [line.split("|") for line in accounting.splitlines()]
            top = next((row for row in rows if row[0] == job), None)
            if top and top[1].split()[0] in terminal:
                break
            if time.monotonic() > deadline:
                raise TimeoutError("Scheduler observation deadline; job state retained, no automatic resubmission")
            time.sleep(15)
        receiver = receipts / "remote"
        (receiver / "experiments/datalad-annex").mkdir(parents=True)
        (receiver / "experiments/cluster").mkdir(parents=True)
        copy(f"{args.host}:{remote}/experiments/cluster/scheduler", receiver / "experiments/cluster")
        copy(f"{args.host}:{remote}/experiments/cluster/logs", receiver / "experiments/cluster")
        copy(f"{args.host}:{remote}/experiments/datalad-annex/outputs", receiver / "experiments/datalad-annex")
        summary.update(scheduler_state=top[1], scheduler_exit_code=top[2])
        if top[1] != "COMPLETED" or top[2] != "0:0":
            raise RuntimeError("Slurm job did not complete successfully")
        summary["oracle"] = verify(receiver)
        local = pd.read_csv(ROOT / "experiments/datalad-annex/outputs/statistics.tsv", sep="\t")
        actual = pd.read_csv(receiver / "experiments/datalad-annex/outputs/statistics.tsv", sep="\t")
        summary["matches_local_numerically"] = bool(
            list(local.columns) == list(actual.columns) and local.shape == actual.shape
            and np.allclose(local.to_numpy(), actual.to_numpy(), rtol=1e-10, atol=1e-11))
        summary["local_table_sha256"] = sha(ROOT / "experiments/datalad-annex/outputs/statistics.tsv")
        summary["remote_lock_sha256_after"] = ssh(shlex.join(["sha256sum", remote + "/pixi.lock"])).split()[0]
        if not summary["oracle"]["ok"] or not summary["matches_local_numerically"]:
            raise RuntimeError("Independent oracle or local numerical comparison failed")
        if summary["remote_lock_sha256_after"] != hashes["pixi.lock"]:
            raise RuntimeError("Remote lock changed")
        summary.update(status="passed", scope="One synthetic CPU job; not full research or repository replay")
    except Exception as error:
        summary.update(status="failed", error=f"{type(error).__name__}: {error}")
        save(receipts / "summary.json", summary)
        raise
    save(receipts / "summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
