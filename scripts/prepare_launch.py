#!/usr/bin/env python3
"""Create, prepare and launch a fresh native session using existing host tools.

Run once under the requested outer duct capture. Never pushes. All generated
evidence belongs in an experiment directory outside the new worker checkout.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run(argv, cwd, capture=False):
    result = subprocess.run([str(x) for x in argv], cwd=cwd, check=True,
                            stdout=subprocess.PIPE if capture else None, text=True)
    return result.stdout.strip() if capture else None


def main():
    defaults_parser = argparse.ArgumentParser(add_help=False)
    defaults_parser.add_argument("--host-config", type=Path, default=Path.home() /
        ".config/stamped-ai-research-next/launch.json")
    preliminary, _ = defaults_parser.parse_known_args()
    defaults = json.loads(preliminary.host_config.read_text()) if preliminary.host_config.is_file() else {}
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host-config", type=Path, default=preliminary.host_config)
    parser.add_argument("--repo", type=Path)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--base", default="main")
    parser.add_argument("--kind", choices=["worktree", "clone"], default="worktree")
    parser.add_argument("--clone-path", type=Path)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--env-manifest", type=Path)
    parser.add_argument("--approved-hooks", type=Path)
    parser.add_argument("--trust-sync", type=Path)
    parser.add_argument("--resolver", type=Path)
    parser.add_argument("--checkpoint-repo")
    parser.add_argument("--annex-remote", default="con-hub")
    parser.add_argument("--annex-git-url")
    parser.add_argument("--annex-url")
    parser.add_argument("--prompt", type=Path, required=True)
    parser.add_argument("--cli", type=Path)
    parser.add_argument("--seconds", type=int, default=240)
    parser.add_argument("--model", default="gpt-6-astra")
    parser.add_argument("--effort", default="ultra")
    parser.add_argument("--codex-home", type=Path,
                        help="Prepared isolated public profile, without private global instructions")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--condition", choices=["baseline", "skills"], default="baseline")
    parser.set_defaults(**defaults)
    args = parser.parse_args()
    for name in ("repo", "env_manifest", "approved_hooks", "trust_sync", "resolver", "cli", "codex_home"):
        value = getattr(args, name)
        if not value:
            parser.error("Missing --" + name.replace("_", "-") + "; configure host defaults once")
        setattr(args, name, Path(value).expanduser().resolve())
    if not args.checkpoint_repo:
        parser.error("Missing --checkpoint-repo; configure host defaults once")
    if not args.annex_git_url or not args.annex_url:
        parser.error("Missing annex remote URLs; configure host defaults once")
    os.environ["CODEX_HOME"] = str(args.codex_home.resolve())
    repo = args.repo.resolve()
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    if not args.branch.startswith("codex/"):
        parser.error("Use a codex/ branch")
    if args.kind == "worktree":
        checkout = repo.parent / (repo.name + "-worktrees") / args.branch
        run(["git", "worktree", "add", "-b", args.branch, checkout, args.base], repo)
    else:
        if not args.clone_path or args.clone_path.exists():
            parser.error("Clone requires an absent --clone-path")
        checkout = args.clone_path.resolve()
        checkout.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", "--no-hardlinks", "--single-branch", "--branch", args.base,
             repo, checkout], repo)
        remote = run(["git", "remote", "get-url", "--push", "origin"], repo, True)
        if not remote.startswith("git@github.com:"):
            raise SystemExit("Source repository must have its configured SSH push remote")
        run(["git", "remote", "set-url", "origin", remote], checkout)
        run(["git", "switch", "-c", args.branch], checkout)
    (evidence / "checkout.json").write_text(json.dumps({"checkout": str(checkout),
        "kind": args.kind, "branch": args.branch, "base": args.base}, indent=2) + "\n")
    run(["git", "submodule", "update", "--init", "--recursive"], checkout)
    lock = args.env_manifest.resolve().with_name("pixi.lock")
    worker_manifest = checkout / "pixi.toml"
    worker_lock = checkout / "pixi.lock"
    if worker_manifest.read_bytes() != args.env_manifest.read_bytes():
        raise SystemExit("Worker manifest differs from the supplied lock's source manifest")
    if worker_lock.exists() and worker_lock.read_bytes() != lock.read_bytes():
        raise SystemExit("Existing worker lock differs; preserve and review")
    shutil.copy2(lock, worker_lock)
    run(["pixi", "install", "--locked", "--manifest-path", worker_manifest], checkout)
    git = ["pixi", "run", "--manifest-path", worker_manifest, "git", "-C", checkout]
    run(git + ["annex", "init"], checkout)
    remotes = run(["git", "remote"], checkout, True).splitlines()
    if args.annex_remote in remotes:
        actual_url = run(["git", "remote", "get-url", args.annex_remote], checkout, True)
        if actual_url != args.annex_git_url:
            raise SystemExit("Existing annex Git URL differs; preserve and review")
    else:
        run(["git", "remote", "add", args.annex_remote, args.annex_git_url], checkout)
    key = "remote." + args.annex_remote + ".annexurl"
    actual_annex = subprocess.run(["git", "config", "--get", key], cwd=checkout,
                                  capture_output=True, text=True)
    if actual_annex.returncode not in (0, 1) or (actual_annex.returncode == 0 and
            actual_annex.stdout.strip() != args.annex_url):
        raise SystemExit("Existing annex endpoint differs; preserve and review")
    run(["git", "config", key, args.annex_url], checkout)
    annex_info = run(git + ["annex", "info", args.annex_remote, "--json"], checkout, True)
    (evidence / "annex-remote.json").write_text(annex_info + "\n")
    (evidence / "environment.json").write_text(json.dumps({"source_manifest": str(args.env_manifest.resolve()),
        "worker_manifest": str(worker_manifest), "worker_lock": str(worker_lock),
        "worker_environment_installed": True,
        "manifest_sha256": hashlib.sha256(args.env_manifest.read_bytes()).hexdigest(),
        "lock_sha256": hashlib.sha256(lock.read_bytes()).hexdigest()}, indent=2) + "\n")
    scripts = Path(__file__).resolve().parent
    run([sys.executable, scripts / "prepare_checkout.py", "--checkout", checkout,
         "--approved-hooks", args.approved_hooks, "--trust-sync", args.trust_sync,
         "--resolver", args.resolver, "--checkpoint-repo", args.checkpoint_repo,
         "--receipt", evidence / "preparation.json"], repo)
    run([sys.executable, scripts / "launch_native_probe.py", "--checkout", checkout,
         "--prompt", args.prompt.resolve(), "--output", evidence / "native",
         "--cli", args.cli, "--seconds", str(args.seconds), "--condition", args.condition,
         "--model", args.model, "--effort", args.effort] +
         (["--preflight-only"] if args.prepare_only else []), repo)


if __name__ == "__main__":
    main()
