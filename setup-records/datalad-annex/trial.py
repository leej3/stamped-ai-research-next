#!/usr/bin/env python3
"""Run the recorded SciPy toy, clean compatibility replays and annex transfer."""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

MODULE = Path("experiments/datalad-annex")
ADAPTER = Path(".agents/skills/datalad-annex/scripts/replay.py")
OUTPUTS = [MODULE / "outputs" / name for name in
           ("statistics.tsv", "figure.svg", "figure.png")]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n")


def verify(repo):
    """Independent known-answer oracle; never rerun the scientific calculation."""
    import csv
    table = repo / OUTPUTS[0]
    if not table.is_file():
        return {"ok": False, "reason": "generated table missing"}
    with table.open(newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    if len(rows) != 1:
        return {"ok": False, "reason": "expected one result row"}
    # Closed-form fixture identities, independent of SciPy and pandas.
    expected = dict(n=5, mean=3, sd=math.sqrt(2.5), t=math.sqrt(18), df=4,
                    p=1 - 36 / (11 * math.sqrt(11)),
                    ci_low=1.036756838522439, ci_high=4.963243161477560)
    comparisons = {key: math.isclose(float(rows[0][key]), value, rel_tol=1e-10, abs_tol=1e-11)
                   for key, value in expected.items()}
    figures = {str(path): (repo / path).is_file() and (repo / path).stat().st_size > 100
               for path in OUTPUTS[1:]}
    return {"ok": all(comparisons.values()) and all(figures.values()),
            "numeric_checks": comparisons, "figures_present": figures,
            "hashes": {str(path): digest(repo / path) for path in OUTPUTS if (repo / path).is_file()}}


class Trial:
    def __init__(self, args):
        self.args = args
        self.root = Path(__file__).resolve().parents[2]
        self.receipts = self.root / MODULE / "receipts" / args.run_id
        if self.receipts.exists():
            raise RuntimeError("Run ID already exists; keep prior evidence")
        self.receipts.mkdir(parents=True)
        self.commands = []
        self.checks = []
        self.external = Path(tempfile.mkdtemp(prefix=f"stamped-datalad-{args.run_id}-"))
        self.lock_hash = digest(self.root / "pixi.lock")
        self.manifest_hash = digest(self.root / "pixi.toml")

    def command(self, argv, cwd=None, expected=(0,)):
        argv = list(map(str, argv))
        number = len(self.commands) + 1
        record = dict(number=number, argv=argv, cwd=str(cwd or self.root),
                      expected_returncodes=list(expected), started_unix=time.time())
        print(f"COMMAND {number}: {json.dumps(argv)}", flush=True)
        stdout, stderr = b"", b""
        try:
            result = subprocess.run(argv, cwd=cwd or self.root, capture_output=True,
                                    timeout=self.args.command_timeout,
                                    env=dict(os.environ, GIT_TERMINAL_PROMPT="0",
                                             DATALAD_UI_PROGRESSBAR="none"))
            stdout, stderr = result.stdout, result.stderr
            record.update(outcome="exited", returncode=result.returncode)
        except subprocess.TimeoutExpired as exc:
            stdout, stderr = exc.stdout or b"", exc.stderr or b""
            record.update(outcome="timeout", returncode=None, error=str(exc))
        except OSError as exc:
            record.update(outcome="spawn_error", returncode=None, error=str(exc))
        record["elapsed_seconds"] = time.time() - record["started_unix"]
        (self.receipts / f"{number:03d}.stdout").write_bytes(stdout)
        (self.receipts / f"{number:03d}.stderr").write_bytes(stderr)
        print(stdout.decode(errors="replace"), end="", flush=True)
        print(stderr.decode(errors="replace"), end="", file=sys.stderr, flush=True)
        self.commands.append(record)
        write_json(self.receipts / "commands.json", self.commands)
        if record["returncode"] not in expected:
            raise RuntimeError(f"Command {number} {record['outcome']}; retained without retry")
        return stdout.decode().strip()

    def pixi(self, repo, *argv, expected=(0,)):
        return self.command(["pixi", "run", "--locked", "--manifest-path", repo / "pixi.toml", *argv],
                            cwd=repo, expected=expected)

    def git(self, repo, *argv):
        return self.pixi(repo, "git", "-C", repo, *argv)

    def check(self, name, passed, **evidence):
        self.checks.append(dict(name=name, passed=bool(passed), **evidence))
        write_json(self.receipts / "checks.json", self.checks)
        if not passed:
            raise RuntimeError(f"Check failed: {name}")

    def clone(self, source, name, revision=None):
        target = self.external / name
        self.command(["git", "clone", "--no-hardlinks", source, target])
        if revision:
            self.command(["git", "-C", target, "checkout", "--detach", revision])
        shutil.copyfile(self.root / "pixi.lock", target / "pixi.lock")
        self.command(["pixi", "install", "--locked", "--manifest-path", target / "pixi.toml"])
        self.check(f"{name}_recorded_environment", digest(target / "pixi.lock") == self.lock_hash
                   and digest(target / "pixi.toml") == self.manifest_hash)
        self.pixi(target, "git", "annex", "init", f"stamped toy {name}")
        self.pixi(target, "python", self.args.initializer, "--checkout", target,
                  "--resolver", self.args.resolver, "--provenance-only", "--receipt",
                  self.receipts / f"{name}-prepared.json")
        return target

    def absent(self, repo, label):
        objects = Path(self.git(repo, "rev-parse", "--git-path", "annex/objects"))
        if not objects.is_absolute():
            objects = repo / objects
        payloads = [str(path.relative_to(objects)) for path in objects.rglob("*") if path.is_file()]
        paths = {str(path): os.path.lexists(repo / path) for path in OUTPUTS}
        self.check(f"{label}_starts_without_outputs_or_payloads", not any(paths.values()) and not payloads,
                   output_paths_exist=paths, annex_payloads=payloads)

    def adapter(self, repo, action, revision, label, base=None):
        argv = ["python", repo / ADAPTER, action, "--dataset", repo,
                "--revision", revision, "--receipt", self.receipts / f"{label}.json"]
        if base:
            argv += ["--onto", base, "--branch", "codex/" + label]
        self.pixi(repo, *argv)
        return json.loads((self.receipts / f"{label}.json").read_text())

    def run(self):
        for path in [ADAPTER, MODULE / "compute.py", MODULE / "input.csv", MODULE / ".gitattributes"]:
            self.git(self.root, "ls-files", "--error-unmatch", path)
        version = self.pixi(self.root, "python", "-c", "import datalad; print(datalad.__version__)")
        self.check("supported_datalad", version == "1.7.1", observed=version)
        self.check("producer_outputs_absent", not any(os.path.lexists(self.root / p) for p in OUTPUTS))
        base = self.git(self.root, "rev-parse", "HEAD")
        write_json(self.receipts / "sources.json", dict(
            base_revision=base, root=str(self.root), external_clones=str(self.external),
            python=sys.executable, manifest_sha256=self.manifest_hash, lock_sha256=self.lock_hash,
            adapter_sha256=digest(self.root / ADAPTER), compute_sha256=digest(self.root / MODULE / "compute.py"),
            initializer=str(self.args.initializer), initializer_sha256=digest(self.args.initializer),
            resolver=str(self.args.resolver), resolver_sha256=digest(self.args.resolver)))
        self.pixi(self.root, "datalad", "run", "--explicit", "-i", MODULE / "input.csv",
                  "-i", MODULE / "compute.py", "-i", "pixi.toml", "-o", MODULE / "outputs",
                  "-m", "compute SciPy known-answer fixture", "--", "python", MODULE / "compute.py")
        revision = self.git(self.root, "rev-parse", "HEAD")
        original = verify(self.root)
        self.check("producer_matches_independent_oracle", original["ok"], **original)
        key = self.git(self.root, "annex", "lookupkey", OUTPUTS[0])
        self.check("table_annexed", bool(key) and (self.root / OUTPUTS[0]).is_symlink(), annex_key=key)
        discovery = self.adapter(self.root, "discover", revision, "discovery")
        self.check("native_unrecognized_compat_discovered", not discovery["native_recognized"]
                   and discovery["ok"], receipt="discovery.json")
        native = self.clone(self.root, "native", base)
        self.absent(native, "native")
        self.pixi(native, "datalad", "rerun", "--onto", base, "--branch", "codex/native",
                  revision, expected=(1,))
        self.check("native_rerun_did_not_generate", not any(os.path.lexists(native / p) for p in OUTPUTS))
        replay = self.clone(self.root, "replay", base)
        self.absent(replay, "replay")
        first = self.adapter(replay, "rerun", revision, "replay", base)
        result = verify(replay)
        self.check("compat_replay_matches_oracle_and_original", result["ok"]
                   and result["hashes"] == original["hashes"], **result)
        replay_revision = first["result_revision"]
        self.adapter(replay, "discover", replay_revision, "replay-discovery")
        second = self.clone(replay, "second-replay", base)
        self.absent(second, "second_replay")
        self.adapter(second, "rerun", replay_revision, "second-replay", base)
        second_result = verify(second)
        self.check("replay_record_itself_replays", second_result["ok"]
                   and second_result["hashes"] == original["hashes"], **second_result)
        noop = self.clone(self.root, "noop", base)
        self.absent(noop, "noop")
        self.pixi(noop, "datalad", "run", "--explicit", "-o", MODULE / "outputs",
                  "-m", "negative no-op control", "--", "python", "-c", "pass")
        negative = verify(noop)
        self.check("zero_exit_noop_rejected", not negative["ok"], verifier=negative)
        receiver = self.clone(self.root, "receiver")
        target = receiver / OUTPUTS[0]
        self.check("receiver_annex_content_absent", target.is_symlink() and not target.exists())
        self.git(receiver, "annex", "get", "--from=origin", OUTPUTS[0])
        self.check("local_annex_retrieval", target.is_file()
                   and digest(target) == original["hashes"][str(OUTPUTS[0])],
                   annex_key=self.git(receiver, "annex", "lookupkey", OUTPUTS[0]),
                   sha256=digest(target), scope="same-host explicit origin; online delivery is separate")
        self.check("lock_unchanged", digest(self.root / "pixi.lock") == self.lock_hash)
        return dict(status="passed", run_revision=revision, base_revision=base,
                    replay_revision=replay_revision, checks=len(self.checks), annex_key=key,
                    external_clones=str(self.external), output_hashes=original["hashes"],
                    lock_sha256=self.lock_hash, online_delivery="handled separately by coordinator",
                    scope="synthetic SciPy/pandas/Matplotlib integration; no scientific efficacy claim")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--initializer", required=True, type=Path)
    parser.add_argument("--resolver", required=True, type=Path)
    parser.add_argument("--command-timeout", type=int, default=180)
    args = parser.parse_args()
    if not args.run_id or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for c in args.run_id):
        parser.error("run-id must contain letters, digits, hyphens or underscores")
    args.initializer = args.initializer.resolve(strict=True)
    args.resolver = args.resolver.resolve(strict=True)
    trial = Trial(args)
    try:
        summary = trial.run()
    except Exception as exc:
        summary = dict(status="failed", error=f"{type(exc).__name__}: {exc}",
                       checks_completed=len(trial.checks), external_clones=str(trial.external),
                       automatic_retry=False)
    write_json(trial.receipts / "summary.json", summary)
    print(json.dumps(summary, indent=2))
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    main()
