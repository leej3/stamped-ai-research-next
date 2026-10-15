#!/usr/bin/env python3
"""Launch one fresh research worker or independent judge with retained evidence."""
import argparse
import hashlib
import json
import os
import re
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
from research_conditions import CONDITION_CHOICES, RESEARCH_SKILLS, canonical_condition

STUDY_SKILLS = ("assess-alignment-with-stamped-principles",) + RESEARCH_SKILLS
JUDGE_SKILLS = {"assess-alignment-with-stamped-principles", "stamped-conventions"}


def selected_skills(role, condition):
    if role == "judge":
        return JUDGE_SKILLS
    return set(RESEARCH_SKILLS) if canonical_condition(condition) == "stamped-explicit" else set()


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


def launch_profile(prepared_profile, assessment_source=None):
    """Isolate each session's installs/history; reuse only host auth and trust.

    Keep host authentication links outside retained evidence. The copied public
    config carries existing exact-path hook approvals; no new trust is granted.
    """
    role = "judge" if assessment_source else "research"
    profile = Path(tempfile.mkdtemp(prefix="stamped-" + role + "-", dir=prepared_profile.parent))
    shutil.copyfile(prepared_profile / "config.toml", profile / "config.toml")
    (profile / "config.toml").chmod(0o600)
    auth = prepared_profile / "auth.json"
    if auth.exists():
        (profile / "auth.json").symlink_to(auth.resolve())
    cache = prepared_profile / "models_cache.json"
    if cache.is_file():
        shutil.copy2(cache, profile / "models_cache.json")
    skills = profile / "skills"
    skills.mkdir()
    if assessment_source:
        for name in sorted(JUDGE_SKILLS):
            (skills / name).symlink_to(assessment_source.resolve() / "skills" / name)
    return profile


def judge_profile(prepared_profile, assessment_source):
    return launch_profile(prepared_profile, assessment_source)


def skill_catalog(preview):
    """Read the native developer catalog, expanding its per-block path aliases."""
    text = preview.decode()
    try:
        messages = json.loads(text)
    except json.JSONDecodeError:
        blocks = [text]  # Plain-text previews from older runtimes/fixtures.
    else:
        if not isinstance(messages, list) or not all(isinstance(message, dict) for message in messages):
            raise SystemExit("Unsupported native prompt preview format")
        blocks = []
        for message in messages:
            if message.get("role") == "developer":
                for item in message.get("content", []):
                    blocks += re.findall(r"<skills_instructions>(.*?)</skills_instructions>",
                                         item.get("text", ""), re.DOTALL)
        if not blocks:
            raise SystemExit("Native preview lacks an inspectable skill catalog")
    catalog = []
    for block in blocks:
        roots = dict(re.findall(r"^- `([^`]+)` = `([^`]+)`\s*$", block, re.MULTILINE))
        entries = re.findall(r"^- ([\w:-]+): .+ \(file: (.+)\)\s*$", block, re.MULTILINE)
        declared = [line for line in block.split("### Available skills")[-1].splitlines()
                    if line.startswith("- ") and not line.startswith("- `")]
        if len(entries) != len(declared):
            raise SystemExit("Unparsed advertised skill entry in native preview")
        for name, raw in entries:
            path = Path(raw)
            if not path.is_absolute() and path.parts and path.parts[0] in roots:
                path = Path(roots[path.parts[0]]).joinpath(*path.parts[1:])
            if not path.is_absolute():
                raise SystemExit("Unresolved advertised skill path: " + raw)
            item = {"name": name, "path": str(path.resolve())}
            if path.is_file():
                item["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            catalog.append(item)
    return catalog


def host_skill_paths(prepared_profile):
    """Refresh exclusions; an old public profile may predate a host install."""
    roots = (Path.home() / ".agents/skills", Path.home() / ".codex/skills",
             Path("/etc/codex/skills"), prepared_profile / "skills")
    return {path for root in roots for path in root.glob("*/SKILL.md")}


def skill_observations(checkout, profile):
    """Inventory installed entrypoints; installation does not establish use."""
    files = []
    for root in (checkout / ".agents/skills", checkout / ".codex/skills", profile / "skills"):
        # Include normal nested installs plus top-level symlinked skill folders.
        for path in sorted(set(root.rglob("SKILL.md")) | set(root.glob("*/SKILL.md"))):
            if path.is_file():
                files.append({"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    return {
        "status": "not-reviewed",
        "evidence": {"events": "events.jsonl", "initial_catalog": "prompt-preflight.json"},
        "installed_entrypoints": files,
        "queries": None, "candidates": None, "selection_rationale": None,
        "source_revisions": None, "installation_cost_and_outcome": None,
        "loaded_instructions": None, "application_evidence": None,
    }


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
    parser.add_argument("--condition", choices=CONDITION_CHOICES, default="baseline")
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--capture-execution", action="store_true")
    args = parser.parse_args()
    if args.seconds < 0 or args.review_seconds < 0:
        parser.error("Time settings must be nonnegative")
    pin = check_assessment(args.assessment_source.resolve(), args.assessment_pin) if args.role == "judge" else None
    if args.role == "research":
        seed = audit_seed(args.checkout.resolve())
        if canonical_condition(seed["condition"]) != canonical_condition(args.condition):
            raise SystemExit("Requested condition differs from the worker seed")
        args.condition = seed["condition"]
        if args.prompt.read_bytes() != research_prompt(args.checkout, args.capture_execution):
            raise SystemExit("Research prompt differs from committed input and common execution guidance")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    prompt = args.prompt.read_bytes()
    (output / "prompt.txt").write_bytes(prompt)
    if args.role == "research":
        assigned = dict(seed.get("assignment", {"condition": seed["condition"],
                        "additional_prompt": "", "legacy_input_version": seed["version"]}))
        assigned.update(prompt_sha256=hashlib.sha256(prompt).hexdigest(),
                        coordinator_commit=seed["coordinator_commit"],
                        supplied_skills_commit=seed.get("skills_commit"),
                        capture_execution=args.capture_execution)
        (output / "condition-assignment.json").write_text(json.dumps(assigned, indent=2) + "\n")
    prepared_profile = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    profile = launch_profile(prepared_profile, args.assessment_source if args.role == "judge" else None)
    config = tomllib.loads((profile / "config.toml").read_text())
    overrides = {item["path"]: item["enabled"] for item in config.get("skills", {}).get("config", [])}
    overrides.update({str(path): False for path in host_skill_paths(prepared_profile)})
    study_skills = ([profile / "skills" / name / "SKILL.md"
                     for name in sorted(JUDGE_SKILLS)] if args.role == "judge" else
                    [args.checkout.resolve() / ".agents/skills" / name / "SKILL.md"
                     for name in STUDY_SKILLS])
    selected = selected_skills(args.role, args.condition)
    if any(not path.is_file() for path in study_skills if path.parent.name in selected):
        raise SystemExit("Selected role requires installed skill entrypoints")
    # Do not disable nonexistent local skill paths in discovery/baseline arms:
    # a worker may spontaneously discover and install them after launch.
    overrides.update({str(path): path.parent.name in selected for path in study_skills if path.is_file()})
    project_skills = set(study_skills)
    if args.role == "judge":
        for directory in (".agents/skills", ".codex/skills"):
            project_skills.update((args.checkout.resolve() / directory).glob("*/SKILL.md"))
        frozen_entries = {p for p in study_skills if p.parent.name in JUDGE_SKILLS}
        overrides.update({str(path): False for path in project_skills - frozen_entries})
    skill_config = "skills.config=[" + ",".join("{path=" + json.dumps(s["path"]) +
                    ",enabled=" + str(s["enabled"]).lower() + "}" for s in
                    ({"path": path, "enabled": enabled} for path, enabled in sorted(overrides.items()))) + "]"
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
    pixi_removed = [key for key in ("PIXI_PROJECT_MANIFEST", "PIXI_IN_SHELL", "PIXI_PROJECT_ROOT",
                    "PIXI_PROJECT_NAME", "PIXI_PROJECT_VERSION", "PIXI_ENVIRONMENT_NAME",
                    "PIXI_ENVIRONMENT_PLATFORMS", "PIXI_PROMPT")
                    if environment.pop(key, None) is not None]
    preview_command = command[:command.index("exec")] + ["-C", str(args.checkout.resolve()),
                      "debug", "prompt-input", prompt.decode()]
    preview = subprocess.run(preview_command, cwd=args.checkout, env=environment,
                             capture_output=True, check=True)
    forbidden = [marker for marker in (b"memory/transport.json", b"sensitive transport configuration",
                b"Hub token file", b"- private-workshop-memory:", b"- workshop-feedback:")
                 if marker in preview.stdout]
    project_instructions = b"# AGENTS.md instructions" in preview.stdout
    catalog = skill_catalog(preview.stdout)
    visible = sorted({item["name"] for item in catalog if item["name"] in STUDY_SKILLS})
    allowed_paths = {str(path.resolve()) for path in study_skills if path.parent.name in selected}
    unexpected = [item for item in catalog if item["path"] not in allowed_paths and
                  not Path(item["path"]).is_relative_to((profile / "skills/.system").resolve())]
    preflight = {"effective_prompt_sha256": hashlib.sha256(preview.stdout).hexdigest(),
                 "private_marker_count": len(forbidden), "condition": args.condition,
                 "role": args.role, "codex_home": str(profile),
                 "project_instructions_present": project_instructions,
                 "visible_study_skills": visible, "advertised_skill_catalog": catalog,
                 "unexpected_skill_catalog": unexpected,
                 "profile_config_sha256": hashlib.sha256((profile / "config.toml").read_bytes()).hexdigest(),
                 "inherited_pixi_variables_removed": pixi_removed}
    (output / "prompt-preflight.json").write_text(json.dumps(preflight, indent=2) + "\n")
    if forbidden or project_instructions or unexpected or set(visible) != selected:
        raise SystemExit("Effective prompt failed instruction or study-skill visibility preflight")
    if args.preflight_only:
        print(json.dumps(preflight))
        return
    record = {"command": command, "cwd": str(args.checkout.resolve()),
              "prompt_sha256": hashlib.sha256(prompt).hexdigest(),
              "inherited_session_variables_removed": removed,
              "inherited_pixi_variables_removed": pixi_removed,
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
    if args.role == "research":
        (output / "skill-observations.json").write_text(json.dumps(
            skill_observations(args.checkout.resolve(), profile), indent=2) + "\n")
    raise SystemExit(124 if timed_out else process.returncode)


if __name__ == "__main__":
    main()
