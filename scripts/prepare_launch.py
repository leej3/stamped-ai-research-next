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


def render_judge_prompt(template, study, target_commit, evidence):
    """Retain the coordinator's scientific brief independently of the target."""
    content = study.read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    (evidence / "study.md").write_bytes(content)
    (evidence / "study.json").write_text(json.dumps({
        "source": str(study.resolve()), "sha256": digest,
    }, indent=2) + "\n")
    prompt = template.read_text().replace("$TARGET_COMMIT", target_commit)
    prompt += ("\nScientific task supplied by the coordinator (SHA-256 " + digest + ").\n"
               "Use this retained brief, not a worker-edited replacement.\n"
               "Relative source links resolve from " + str(study.resolve().parent) + ".\n\n"
               + content.decode())
    destination = evidence / "judge-prompt.md"
    destination.write_text(prompt)
    return destination


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
    parser.add_argument("--base", required=True,
                        help="Clean starting ref for research, exact result ref for judging")
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
    parser.add_argument("--prompt", type=Path)
    parser.add_argument("--study", type=Path,
                        help="Coordinator's frozen scientific brief; required for judging")
    parser.add_argument("--cli", type=Path)
    parser.add_argument("--seconds", type=int, default=0,
                        help="Explicit hard limit; 0 waits for completion")
    parser.add_argument("--review-seconds", type=int, default=5400)
    parser.add_argument("--model", default="gpt-6-luna")
    parser.add_argument("--effort", default="high")
    parser.add_argument("--role", choices=["research", "judge"], default="research")
    parser.add_argument("--codex-home", type=Path,
                        help="Prepared isolated public profile, without private global instructions")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--condition", choices=["baseline", "skills"], default="baseline")
    parser.set_defaults(**defaults)
    args = parser.parse_args()
    if args.seconds < 0 or args.review_seconds < 0:
        parser.error("Time settings must be nonnegative")
    if args.role == "research" and not args.prompt:
        parser.error("Research workers require --prompt")
    if args.role == "judge" and (args.prompt or args.condition != "baseline"):
        parser.error("Judges use the fixed template; omit --prompt and --condition")
    if args.role == "judge" and (not args.study or not args.study.is_file()):
        parser.error("Judges require --study pointing to the frozen scientific brief")
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
    base_commit = run(["git", "rev-parse", "--verify", args.base + "^{commit}"], repo, True)
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    if not args.branch.startswith("codex/"):
        parser.error("Use a codex/ branch")
    if args.role == "judge":
        template = Path(__file__).resolve().parents[1] / "judge-prompt.md"
        args.prompt = render_judge_prompt(template, args.study, base_commit, evidence)
    if args.kind == "worktree":
        checkout = repo.parent / (repo.name + "-worktrees") / args.branch
        run(["git", "worktree", "add", "-b", args.branch, checkout, base_commit], repo)
    else:
        if not args.clone_path or args.clone_path.exists():
            parser.error("Clone requires an absent --clone-path")
        checkout = args.clone_path.resolve()
        checkout.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", "--no-hardlinks", "--no-checkout",
             repo, checkout], repo)
        remote = run(["git", "remote", "get-url", "--push", "origin"], repo, True)
        if not remote.startswith("git@github.com:"):
            raise SystemExit("Source repository must have its configured SSH push remote")
        run(["git", "remote", "set-url", "origin", remote], checkout)
        run(["git", "checkout", "--detach", base_commit], checkout)
        run(["git", "switch", "-c", args.branch], checkout)
    if run(["git", "rev-parse", "HEAD"], checkout, True) != base_commit:
        raise SystemExit("Existing worker checkout does not match the requested starting commit")
    if run(["git", "status", "--porcelain"], checkout, True):
        raise SystemExit("Worker checkout has existing changes; use a fresh branch")
    (evidence / "checkout.json").write_text(json.dumps({"checkout": str(checkout),
        "kind": args.kind, "branch": args.branch, "base": args.base,
        "base_commit": base_commit, "role": args.role}, indent=2) + "\n")
    run(["git", "submodule", "update", "--init", "--recursive"], checkout)
    lock = args.env_manifest.resolve().with_name("pixi.lock")
    # Judges use prepared operational tools; the target's environment is tested
    # only by the separately authorized replay, never repaired during judging.
    worker_manifest = args.env_manifest if args.role == "judge" else checkout / "pixi.toml"
    worker_lock = lock if args.role == "judge" else checkout / "pixi.lock"
    if args.role != "judge" and worker_manifest.read_bytes() != args.env_manifest.read_bytes():
        raise SystemExit("Worker manifest differs from the supplied lock's source manifest")
    if worker_lock.exists() and worker_lock.read_bytes() != lock.read_bytes():
        raise SystemExit("Existing worker lock differs; preserve and review")
    if lock != worker_lock:
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
         "--review-seconds", str(args.review_seconds), "--role", args.role,
         "--assessment-pin", scripts.parent / "assessment-version.json",
         "--model", args.model, "--effort", args.effort] +
         (["--preflight-only"] if args.prepare_only else []), repo)


if __name__ == "__main__":
    main()
