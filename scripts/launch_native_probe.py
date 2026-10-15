#!/usr/bin/env python3
"""Launch one bounded fresh native Codex process under the caller's duct capture."""
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--prompt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cli", type=Path, required=True)
    parser.add_argument("--seconds", type=int, default=240)
    parser.add_argument("--model", default="gpt-6-astra")
    parser.add_argument("--effort", default="ultra")
    parser.add_argument("--condition", choices=["baseline", "skills"], default="baseline")
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    prompt = args.prompt.read_bytes()
    (output / "prompt.txt").write_bytes(prompt)
    profile = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    config = tomllib.loads((profile / "config.toml").read_text())
    overrides = list(config.get("skills", {}).get("config", []))
    study_skills = [args.checkout.resolve() / ".agents/skills" / name / "SKILL.md" for name in
                    ("assess-alignment-with-stamped-principles", "align-with-stamped-principles",
                     "stamped-conventions", "create-stamped-project",
                     "create-repronim-stamped-project", "do-full-research-loop")]
    if args.condition == "skills" and not all(path.is_file() for path in study_skills):
        raise SystemExit("Skills condition requires all pinned project study skill entrypoints")
    overrides += [{"path": str(path), "enabled": args.condition == "skills"} for path in study_skills]
    skill_config = "skills.config=[" + ",".join("{path=" + json.dumps(s["path"]) +
                    ",enabled=" + str(s["enabled"]).lower() + "}" for s in overrides) + "]"
    command = [str(args.cli), "--no-daemon", "-a", "never", "-s", "danger-full-access",
               "-m", args.model, "-c", 'model_reasoning_effort="' + args.effort + '"',
               "-c", skill_config,
               "exec", "--json", "--color", "never", "-C", str(args.checkout.resolve()),
               "-o", str(output / "final.txt"), "-"]
    environment = os.environ.copy()
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
                 "visible_study_skills": visible}
    (output / "prompt-preflight.json").write_text(json.dumps(preflight, indent=2) + "\n")
    if forbidden or (args.condition == "baseline" and visible) or (args.condition == "skills" and len(visible) != len(study_skills)):
        raise SystemExit("Effective prompt failed privacy or study-skill visibility preflight")
    if args.preflight_only:
        print(json.dumps(preflight))
        return
    record = {"command": command, "cwd": str(args.checkout.resolve()),
              "prompt_sha256": hashlib.sha256(prompt).hexdigest(),
              "inherited_session_variables_removed": removed,
              "started_at": datetime.now(timezone.utc).isoformat(), "timeout_seconds": args.seconds}
    record["condition"] = args.condition
    record["codex_home"] = str(profile)
    record["study_skill_paths"] = [str(p) for p in study_skills]
    (output / "launch.json").write_text(json.dumps(record, indent=2) + "\n")
    started = time.monotonic()
    process = subprocess.Popen(command, cwd=args.checkout, env=environment,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               process_group=0)
    def relay():
        with (output / "events.jsonl").open("xb") as events:
            for line in process.stdout:
                events.write(line)
                events.flush()
                sys.stdout.buffer.write(line)
                sys.stdout.buffer.flush()
    reader = threading.Thread(target=relay)
    reader.start()
    process.stdin.write(prompt)
    process.stdin.close()
    timed_out = False
    try:
        process.wait(timeout=args.seconds)
    except subprocess.TimeoutExpired:
        timed_out = True
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
    if reader.is_alive():
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
