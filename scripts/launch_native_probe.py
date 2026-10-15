#!/usr/bin/env python3
"""Launch one fresh research worker or independent judge with retained evidence."""
import argparse
import hashlib
import json
import os
import signal
import subprocess
import sys
import threading
import time
import tomllib
from datetime import datetime, timezone
from pathlib import Path

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


def check_assessment(checkout, expected_pin):
    """Check the judge's sources against the coordinator's independent pin."""
    pin = json.loads(expected_pin.read_text())
    if json.loads((checkout / "assessment-version.json").read_text()) != pin:
        raise SystemExit("Target assessment pin differs from the fixed judge configuration")
    source = checkout / "assessment"
    head = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    dirty = subprocess.check_output(["git", "-C", str(source), "status", "--porcelain"])
    if head != pin["source_commit"] or dirty:
        raise SystemExit("Judge assessment source is changed or at the wrong revision")
    modules = subprocess.check_output(["git", "-C", str(source), "submodule", "status", "--recursive"])
    if any(line[:1] != b" " for line in modules.splitlines()):
        raise SystemExit("Judge assessment dependencies differ from their recorded revisions")
    for name in JUDGE_SKILLS:
        actual = (checkout / ".agents/skills" / name / "SKILL.md").resolve()
        expected = (source / "skills" / name / "SKILL.md").resolve()
        if actual != expected or not actual.is_file():
            raise SystemExit("Judge entrypoint does not resolve to the frozen assessment")
    return pin


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
    parser.add_argument("--condition", choices=["baseline", "skills"], default="baseline")
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    if args.seconds < 0 or args.review_seconds < 0:
        parser.error("Time settings must be nonnegative")
    pin = check_assessment(args.checkout.resolve(), args.assessment_pin) if args.role == "judge" else None
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    prompt = args.prompt.read_bytes()
    (output / "prompt.txt").write_bytes(prompt)
    profile = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    config = tomllib.loads((profile / "config.toml").read_text())
    overrides = list(config.get("skills", {}).get("config", []))
    study_skills = [args.checkout.resolve() / ".agents/skills" / name / "SKILL.md"
                    for name in STUDY_SKILLS]
    selected = selected_skills(args.role, args.condition)
    if any(not path.is_file() for path in study_skills if path.parent.name in selected):
        raise SystemExit("Selected role requires installed skill entrypoints")
    overrides += [{"path": str(path), "enabled": path.parent.name in selected} for path in study_skills]
    skill_config = "skills.config=[" + ",".join("{path=" + json.dumps(s["path"]) +
                    ",enabled=" + str(s["enabled"]).lower() + "}" for s in overrides) + "]"
    command = [str(args.cli), "--no-daemon", "-a", "never", "-s", "danger-full-access",
               "-m", args.model, "-c", 'model_reasoning_effort="' + args.effort + '"',
               "-c", skill_config,
               "exec", "--json", "--color", "never", "-C", str(args.checkout.resolve()),
               "-o", str(output / "final.txt"), "-"]
    environment = os.environ.copy()
    if args.role == "judge":
        report_dir = output / "judgment"
        report_dir.mkdir()
        environment["STAMPED_JUDGE_OUTPUT"] = str(report_dir)
        environment["STAMPED_JUDGE_TARGET"] = str(args.checkout.resolve())
        environment["STAMPED_ASSESSMENT_RUNNER"] = str(Path(__file__).resolve().with_name("assessment.py"))
        environment["STAMPED_ASSESSMENT_PYTHON"] = sys.executable
    removed = [key for key in ("CODEX_THREAD_ID", "CODEX_PARENT_THREAD_ID", "CODEX_SESSION_ID")
               if environment.pop(key, None) is not None]
    preview_command = command[:command.index("exec")] + ["-C", str(args.checkout.resolve()),
                      "debug", "prompt-input", prompt.decode()]
    preview = subprocess.run(preview_command, cwd=args.checkout, env=environment,
                             capture_output=True, check=True)
    forbidden = [marker for marker in (b"memory/transport.json", b"sensitive transport configuration",
                b"Hub token file", b"- private-workshop-memory:", b"- workshop-feedback:")
                 if marker in preview.stdout]
    visible = [p.parent.name for p in study_skills
               if ("- " + p.parent.name + ":").encode() in preview.stdout]
    preflight = {"effective_prompt_sha256": hashlib.sha256(preview.stdout).hexdigest(),
                 "private_marker_count": len(forbidden), "condition": args.condition,
                 "role": args.role,
                 "visible_study_skills": visible}
    (output / "prompt-preflight.json").write_text(json.dumps(preflight, indent=2) + "\n")
    if forbidden or set(visible) != selected:
        raise SystemExit("Effective prompt failed privacy or study-skill visibility preflight")
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
