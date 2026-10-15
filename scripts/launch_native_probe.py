#!/usr/bin/env python3
"""Launch one fresh research worker or independent judge with retained evidence."""
import argparse
import hashlib
import json
import os
import signal
import shutil
import tempfile
import subprocess
import sys
import threading
import time
import tomllib
from datetime import datetime, timezone
from pathlib import Path

from study_seed import audit_seed, research_prompt

STUDY_SKILLS = (
    "assess-alignment-with-stamped-principles", "align-with-stamped-principles",
    "stamped-conventions", "create-stamped-project",
    "create-repronim-stamped-project", "do-full-research-loop", "pixi-with-stamped",
)
JUDGE_SKILLS = {"assess-alignment-with-stamped-principles", "stamped-conventions"}


def selected_skills(role, condition):
    if role == "judge":
        return JUDGE_SKILLS
    if condition == "baseline":
        return set()
    return set(STUDY_SKILLS) - {"assess-alignment-with-stamped-principles"}


def check_assessment(source, expected_pin):
    """Check external coordinator sources, never a worker-supplied assessor."""
    pin = json.loads(expected_pin.read_text())
    head = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    dirty = subprocess.check_output(["git", "-C", str(source), "status", "--porcelain"])
    if head != pin["source_commit"] or dirty:
        raise SystemExit("Judge assessment source is changed or at the wrong revision")
    modules = subprocess.check_output(["git", "-C", str(source), "submodule", "status", "--recursive"])
    if any(line[:1] != b" " for line in modules.splitlines()):
        raise SystemExit("Judge assessment dependencies differ from their recorded revisions")
    if any(not (source / "skills" / name / "SKILL.md").is_file() for name in JUDGE_SKILLS):
        raise SystemExit("Frozen assessment skill entrypoint is missing")
    return pin


def judge_profile(prepared_profile, assessment_source):
    """Discover frozen skills in a per-judge catalog without touching the target.

    Keep host authentication links outside retained evidence. The copied public
    config carries existing exact-path hook approvals; no new trust is granted.
    """
    profile = Path(tempfile.mkdtemp(prefix="stamped-judge-", dir=prepared_profile.parent))
    shutil.copyfile(prepared_profile / "config.toml", profile / "config.toml")
    (profile / "config.toml").chmod(0o600)
    for name in ("auth.json", "models_cache.json"):
        source = prepared_profile / name
        if source.exists():
            (profile / name).symlink_to(source.resolve())
    skills = profile / "skills"
    skills.mkdir()
    for name in sorted(JUDGE_SKILLS):
        (skills / name).symlink_to(assessment_source.resolve() / "skills" / name)
    return profile


def wait_for_worker(process, output, hard_limit, review_after):
    """A review notification does not terminate useful work; limits are opt-in."""
    started = time.monotonic()
    deadline = started + hard_limit if hard_limit else None
    review = started + review_after if review_after else None
    while True:
        now = time.monotonic()
        pending = [t for t in (deadline, review) if t is not None]
        timeout = max(0, min(pending) - now) if pending else None
        try:
            process.wait(timeout=timeout)
            return False
        except subprocess.TimeoutExpired:
            now = time.monotonic()
            if review is not None and now >= review:
                receipt = {"event": "review_due", "elapsed_seconds": now - started,
                           "pid": process.pid, "terminated": False}
                (output / "review.json").write_text(json.dumps(receipt, indent=2) + "\n")
                print(json.dumps(receipt), file=sys.stderr, flush=True)
                review = None
            if deadline is not None and now >= deadline:
                return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--prompt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cli", type=Path, required=True)
    parser.add_argument("--seconds", type=int, default=0,
                        help="Explicit hard limit; 0 (default) waits for completion")
    parser.add_argument("--review-seconds", type=int, default=5400,
                        help="Emit a progress-review receipt without stopping; 0 disables")
    parser.add_argument("--model", default="gpt-6-luna")
    parser.add_argument("--effort", default="high")
    parser.add_argument("--role", choices=["research", "judge"], default="research")
    parser.add_argument("--assessment-pin", type=Path,
                        default=Path(__file__).resolve().parents[1] / "assessment-version.json")
    parser.add_argument("--assessment-source", type=Path,
                        default=Path(__file__).resolve().parents[1] / "assessment")
    parser.add_argument("--condition", choices=["baseline", "skills"], default="baseline")
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    if args.seconds < 0 or args.review_seconds < 0:
        parser.error("Time settings must be nonnegative")
    pin = check_assessment(args.assessment_source.resolve(), args.assessment_pin) if args.role == "judge" else None
    if args.role == "research":
        seed = audit_seed(args.checkout.resolve())
        if seed["condition"] != args.condition:
            raise SystemExit("Requested condition differs from the worker seed")
        if args.prompt.read_bytes() != research_prompt(args.checkout):
            raise SystemExit("Research prompt differs from committed input and common execution guidance")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    prompt = args.prompt.read_bytes()
    (output / "prompt.txt").write_bytes(prompt)
    prepared_profile = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    profile = (judge_profile(prepared_profile, args.assessment_source)
               if args.role == "judge" else prepared_profile)
    config = tomllib.loads((profile / "config.toml").read_text())
    overrides = list(config.get("skills", {}).get("config", []))
    study_skills = ([profile / "skills" / name / "SKILL.md"
                     for name in sorted(JUDGE_SKILLS)] if args.role == "judge" else
                    [args.checkout.resolve() / ".agents/skills" / name / "SKILL.md"
                     for name in STUDY_SKILLS])
    selected = selected_skills(args.role, args.condition)
    if any(not path.is_file() for path in study_skills if path.parent.name in selected):
        raise SystemExit("Selected role requires installed skill entrypoints")
    overrides += [{"path": str(path), "enabled": path.parent.name in selected} for path in study_skills]
    project_skills = set(study_skills)
    if args.role == "judge":
        for directory in (".agents/skills", ".codex/skills"):
            project_skills.update((args.checkout.resolve() / directory).glob("*/SKILL.md"))
        frozen_entries = {p for p in study_skills if p.parent.name in JUDGE_SKILLS}
        overrides += [{"path": str(path), "enabled": False}
                      for path in sorted(project_skills - frozen_entries)]
    skill_config = "skills.config=[" + ",".join("{path=" + json.dumps(s["path"]) +
                    ",enabled=" + str(s["enabled"]).lower() + "}" for s in overrides) + "]"
    command = [str(args.cli), "--no-daemon", "-a", "never", "-s", "danger-full-access",
               "-m", args.model, "-c", 'model_reasoning_effort="' + args.effort + '"',
               "-c", skill_config, "-c", "project_doc_max_bytes=0",
               "exec", "--json", "--color", "never", "-C", str(args.checkout.resolve()),
               "-o", str(output / "final.txt"), "-"]
    environment = os.environ.copy()
    environment["CODEX_HOME"] = str(profile)
    if args.role == "judge":
        report_dir = output / "judgment"
        report_dir.mkdir()
        environment["STAMPED_JUDGE_OUTPUT"] = str(report_dir)
        environment["STAMPED_JUDGE_TARGET"] = str(args.checkout.resolve())
        environment["STAMPED_ASSESSMENT_RUNNER"] = str(Path(__file__).resolve().with_name("assessment.py"))
        environment["STAMPED_ASSESSMENT_PYTHON"] = sys.executable
        environment["STAMPED_ASSESSMENT_SOURCE"] = str(args.assessment_source.resolve())
        environment["STAMPED_ASSESSMENT_PIN"] = str(args.assessment_pin.resolve())
    removed = [key for key in ("CODEX_THREAD_ID", "CODEX_PARENT_THREAD_ID", "CODEX_SESSION_ID")
               if environment.pop(key, None) is not None]
    preview_command = command[:command.index("exec")] + ["-C", str(args.checkout.resolve()),
                      "debug", "prompt-input", prompt.decode()]
    preview = subprocess.run(preview_command, cwd=args.checkout, env=environment,
                             capture_output=True, check=True)
    forbidden = [marker for marker in (b"memory/transport.json", b"sensitive transport configuration",
                b"Hub token file", b"- private-workshop-memory:", b"- workshop-feedback:")
                 if marker in preview.stdout]
    project_instructions = b"# AGENTS.md instructions" in preview.stdout
    visible = sorted({p.parent.name for p in project_skills
                      if ("- " + p.parent.name + ":").encode() in preview.stdout})
    preflight = {"effective_prompt_sha256": hashlib.sha256(preview.stdout).hexdigest(),
                 "private_marker_count": len(forbidden), "condition": args.condition,
                 "role": args.role, "codex_home": str(profile),
                 "project_instructions_present": project_instructions,
                 "visible_study_skills": visible}
    (output / "prompt-preflight.json").write_text(json.dumps(preflight, indent=2) + "\n")
    if forbidden or project_instructions or set(visible) != selected:
        raise SystemExit("Effective prompt failed instruction or study-skill visibility preflight")
    if args.preflight_only:
        print(json.dumps(preflight))
        return
    record = {"command": command, "cwd": str(args.checkout.resolve()),
              "prompt_sha256": hashlib.sha256(prompt).hexdigest(),
              "inherited_session_variables_removed": removed,
              "started_at": datetime.now(timezone.utc).isoformat(), "timeout_seconds": args.seconds,
              "review_seconds": args.review_seconds, "role": args.role,
              "assessment_pin": pin}
    record["condition"] = args.condition if args.role == "research" else None
    record["codex_home"] = str(profile)
    record["study_skill_paths"] = [str(p) for p in study_skills]
    record["starting_commit"] = subprocess.check_output(
        ["git", "-C", str(args.checkout), "rev-parse", "HEAD"], text=True).strip()
    if args.role == "judge":
        runner = Path(environment["STAMPED_ASSESSMENT_RUNNER"])
        record["assessment_runner_sha256"] = hashlib.sha256(runner.read_bytes()).hexdigest()
    (output / "launch.json").write_text(json.dumps(record, indent=2) + "\n")
    started = time.monotonic()
    process = subprocess.Popen(command, cwd=args.checkout, env=environment,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               process_group=0)
    def relay():
        with (output / "events.jsonl").open("xb") as events:
            for line in process.stdout:
                events.write(line)
                events.flush()
                sys.stdout.buffer.write(line)
                sys.stdout.buffer.flush()
    reader = threading.Thread(target=relay)
    def relay_errors():
        with (output / "stderr.txt").open("xb") as errors:
            for line in process.stderr:
                errors.write(line)
                errors.flush()
                sys.stderr.buffer.write(line)
                sys.stderr.buffer.flush()
    error_reader = threading.Thread(target=relay_errors)
    reader.start()
    error_reader.start()
    process.stdin.write(prompt)
    process.stdin.close()
    timed_out = wait_for_worker(process, output, args.seconds, args.review_seconds)
    if timed_out:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        time.sleep(5)
        # Always kill the group after the grace period, even if its leader exited.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()
    reader.join(timeout=10)
    error_reader.join(timeout=10)
    if reader.is_alive() or error_reader.is_alive():
        raise SystemExit("A descendant retained the output pipe; inspect retained process logs")
    record.update({"finished_at": datetime.now(timezone.utc).isoformat(),
                   "elapsed_seconds": time.monotonic() - started,
                   "timed_out": timed_out, "returncode": process.returncode,
                   "limitation": "Detached descendants outside the process group are not forcibly contained."})
    sessions = []
    for line in (output / "events.jsonl").read_text().splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if item.get("type") == "thread.started":
            sessions.append(item.get("thread_id"))
    record["native_session_ids"] = sessions
    (output / "result.json").write_text(json.dumps(record, indent=2) + "\n")
    raise SystemExit(124 if timed_out else process.returncode)


if __name__ == "__main__":
    main()
