#!/usr/bin/env python3
"""Cold recipient integration driver; uses the published scientific code/oracle."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


MODULE = Path(__file__).resolve().parent
ROOT = MODULE.parents[1]
RECEIPTS = MODULE / "receipts"
PUBLIC = "https://github.com/leej3/stamped-ai-research-next.git"
RESOLVER = Path("/Users/johnlee/.agents/skills/commit-provenance/scripts/resolve.sh")
INITIALIZER = ROOT / "scripts/prepare_checkout.py"
VERIFIER = ROOT / "experiments/datalad-annex/verify.py"
ADAPTER = ROOT / ".agents/skills/datalad-annex/scripts/replay.py"
EXPECTED = ROOT / "experiments/datalad-annex/receipts/toy-001/summary.json"
SOURCE = json.loads((MODULE / "source.json").read_text())
ORIGINAL = json.loads(EXPECTED.read_text())
COMMANDS = []
CHECKS = []


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(argv, cwd=ROOT, expected=(0,)):
    argv = list(map(str, argv))
    number = len(COMMANDS) + 1
    rec = dict(number=number, argv=argv, cwd=str(cwd),
               expected_returncodes=list(expected), started_unix=time.time())
    print(f"COMMAND {number}: {json.dumps(argv)}", flush=True)
    stdout = stderr = b""
    try:
        result = subprocess.run(argv, cwd=cwd, capture_output=True, timeout=300,
                                env=dict(os.environ, GIT_TERMINAL_PROMPT="0",
                                         DATALAD_UI_PROGRESSBAR="none"))
        stdout, stderr = result.stdout, result.stderr
        rec.update(outcome="exited", returncode=result.returncode)
    except subprocess.TimeoutExpired as exc:
        stdout, stderr = exc.stdout or b"", exc.stderr or b""
        rec.update(outcome="timeout", returncode=None, error=str(exc))
    except OSError as exc:
        rec.update(outcome="spawn_error", returncode=None, error=str(exc))
    rec["elapsed_seconds"] = time.time() - rec["started_unix"]
    (RECEIPTS / f"{number:03d}.stdout").write_bytes(stdout)
    (RECEIPTS / f"{number:03d}.stderr").write_bytes(stderr)
    print(stdout.decode(errors="replace"), end="", flush=True)
    print(stderr.decode(errors="replace"), end="", file=sys.stderr, flush=True)
    COMMANDS.append(rec)
    write(RECEIPTS / "commands.json", COMMANDS)
    if rec["returncode"] not in expected:
        raise RuntimeError(f"Command {number} {rec['outcome']}; evidence retained without retry")
    return stdout.decode().strip()


def pixi(repo, *argv, expected=(0,)):
    return command(["pixi", "run", "--locked", "--manifest-path", repo / "pixi.toml", *argv],
                   cwd=repo, expected=expected)


def check(name, passed, **evidence):
    CHECKS.append(dict(name=name, passed=bool(passed), **evidence))
    write(RECEIPTS / "checks.json", CHECKS)
    if not passed:
        raise RuntimeError(f"Check failed: {name}")


def prepare(name):
    repo = ROOT.parent / (name + "-002")
    command(["git", "clone", "--no-local", "--branch", "main", "--recurse-submodules",
             PUBLIC, repo])
    command(["git", "-C", repo, "checkout", "--detach", ORIGINAL["base_revision"]])
    command(["git", "-C", repo, "submodule", "update", "--init", "--recursive"])
    check(name + "_clean_checkout", not command(["git", "-C", repo, "status", "--porcelain"]))
    shutil.copyfile(ROOT / "pixi.lock", repo / "pixi.lock")
    check(name + "_recorded_environment",
          sha(repo / "pixi.lock") == SOURCE["lock_sha256"]
          and sha(repo / "pixi.toml") == SOURCE["manifest_sha256"],
          lock_sha256=sha(repo / "pixi.lock"), manifest_sha256=sha(repo / "pixi.toml"))
    command(["pixi", "install", "--locked", "--manifest-path", repo / "pixi.toml"], cwd=repo)
    pixi(repo, "git", "annex", "init", "cold public recipient " + name)
    pixi(repo, "python", INITIALIZER, "--checkout", repo, "--resolver", RESOLVER,
         "--provenance-only", "--receipt", RECEIPTS / (name + "-prepared.json"))
    pixi(repo, "python", VERIFIER, repo, "--expect-absent", "--receipt",
         RECEIPTS / (name + "-absent.json"))
    return repo


def run():
    check("exact_public_lock", sha(ROOT / "pixi.lock") == ORIGINAL["lock_sha256"])
    check("stable_helper_files", all(p.is_file() for p in (INITIALIZER, VERIFIER, ADAPTER)))
    command(["duct", "--version"])
    version = pixi(ROOT, "python", "-c", "import datalad; print(datalad.__version__)")
    check("supported_datalad", version == "1.7.1", observed=version)
    replay = prepare("replay")
    pixi(replay, "python", ADAPTER, "discover", "--dataset", replay,
         "--revision", ORIGINAL["run_revision"], "--receipt", RECEIPTS / "discovery.json")
    discovery = json.loads((RECEIPTS / "discovery.json").read_text())
    check("native_unrecognized_compatibility_discovered", discovery["ok"]
          and not discovery["native_recognized"])
    native_output = pixi(replay, "datalad", "rerun", "--onto", ORIGINAL["base_revision"],
         "--branch", "codex/recipient-cold-native", ORIGINAL["run_revision"], expected=(1,))
    check("native_failed_for_undiscovered_record", "No run commits found" in native_output, output=native_output)
    pixi(replay, "python", VERIFIER, replay, "--expect-absent", "--receipt",
         RECEIPTS / "after-native-absent.json")
    pixi(replay, "python", ADAPTER, "rerun", "--dataset", replay,
         "--revision", ORIGINAL["run_revision"], "--onto", ORIGINAL["base_revision"],
         "--branch", "codex/recipient-cold-replay", "--receipt", RECEIPTS / "replay.json")
    pixi(replay, "python", VERIFIER, replay, "--expected-summary", EXPECTED,
         "--receipt", RECEIPTS / "independent-result.json")
    result = json.loads((RECEIPTS / "independent-result.json").read_text())
    check("replayed_outputs_match_independent_oracle_and_original_hashes", result["ok"]
          and result["hashes_match_original"], verifier="independent-result.json")
    revision = pixi(replay, "git", "rev-parse", "HEAD")
    message = pixi(replay, "git", "show", "-s", "--format=%B", revision)
    check("replay_commit_record_and_fresh_provenance", message.startswith("feat: record DataLad run\n")
          and "[DATALAD RUNCMD]" in message and "Co-Authored-By: Codex Desktop " in message
          and "Codex-Reasoning-Effort: " in message and "unavailable" not in message.lower(),
          revision=revision, message_sha256=hashlib.sha256(message.encode()).hexdigest(),
          note="Published prepared hook invokes exact resolver immediately for each authored commit.")
    pixi(replay, "python", ADAPTER, "discover", "--dataset", replay,
         "--revision", revision, "--receipt", RECEIPTS / "replay-discovery.json")
    noop = prepare("noop")
    pixi(noop, "datalad", "run", "--explicit", "-o", "experiments/datalad-annex/outputs",
         "-m", "negative no-op control", "--", "python", "-c", "pass")
    pixi(noop, "python", VERIFIER, noop, "--expected-summary", EXPECTED,
         "--receipt", RECEIPTS / "noop-result.json", expected=(1,))
    negative = json.loads((RECEIPTS / "noop-result.json").read_text())
    check("zero_exit_noop_rejected", not negative["ok"], verifier="noop-result.json")
    for name, repo in (("published", ROOT), ("replay", replay), ("noop", noop)):
        check(name + "_lock_and_manifest_unchanged", sha(repo / "pixi.lock") == SOURCE["lock_sha256"]
              and sha(repo / "pixi.toml") == SOURCE["manifest_sha256"])
    return dict(status="passed", checks=len(CHECKS), subprocesses=len(COMMANDS),
                source_revision=SOURCE["published_revision"], run_revision=ORIGINAL["run_revision"],
                base_revision=ORIGINAL["base_revision"], replay_revision=revision,
                replay_branch="codex/recipient-cold-replay", replay_clone=str(replay),
                noop_clone=str(noop), stable_checkout=str(ROOT),
                environment_revision=SOURCE["environment_revision"],
                lock_sha256=SOURCE["lock_sha256"], output_hashes=result["hashes"],
                native_rerun="expected failure: prefixed record unrecognized",
                no_op="zero-exit command rejected by same independent verifier",
                obstacles=[SOURCE["setup_correction"]], scope="cold public-clone synthetic integration; no scientific efficacy claim")


def main():
    RECEIPTS.mkdir()
    started = time.time()
    try:
        summary = run()
    except Exception as exc:
        summary = dict(status="failed", error=f"{type(exc).__name__}: {exc}",
                       checks_completed=len(CHECKS), subprocesses=len(COMMANDS),
                       automatic_retry=False, source=SOURCE)
    summary["elapsed_seconds"] = time.time() - started
    write(RECEIPTS / "summary.json", summary)
    print(json.dumps(summary, indent=2), flush=True)
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
