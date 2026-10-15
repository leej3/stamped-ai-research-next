"""Launcher regressions using local fixtures, never a live research agent."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("launch", ROOT / "scripts/launch_native_probe.py")
launch = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(launch)


def test_roles_do_not_leak_stamped_guidance():
    assert launch.selected_skills("research", "baseline") == set()
    treatment = launch.selected_skills("research", "skills")
    assert "pixi-with-stamped" in treatment
    assert "assess-alignment-with-stamped-principles" not in treatment
    assert launch.selected_skills("judge", "baseline") == {
        "assess-alignment-with-stamped-principles", "stamped-conventions"}


def test_review_does_not_terminate_worker(tmp_path):
    process = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(.15)"])
    try:
        assert not launch.wait_for_worker(process, tmp_path, 0, .01)
        assert process.returncode == 0
        receipt = json.loads((tmp_path / "review.json").read_text())
        assert receipt["terminated"] is False
    finally:
        if process.poll() is None:
            process.kill()
        process.wait()


def test_explicit_limit_remains_available(tmp_path):
    process = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    try:
        assert launch.wait_for_worker(process, tmp_path, .01, 0)
        assert not (tmp_path / "review.json").exists()
    finally:
        process.kill()
        process.wait()


def test_target_cannot_supply_a_different_assessment_pin(tmp_path):
    pin = json.loads((ROOT / "assessment-version.json").read_text())
    pin["source_commit"] = "0" * 40
    expected = tmp_path / "pin.json"
    expected.write_text(json.dumps(pin))
    with pytest.raises(SystemExit, match="Target assessment pin differs"):
        launch.check_assessment(ROOT, expected)


def test_changed_assessor_revision_is_rejected(monkeypatch):
    def output(argv, **kwargs):
        return "wrong\n" if "rev-parse" in argv else b""
    monkeypatch.setattr(launch.subprocess, "check_output", output)
    with pytest.raises(SystemExit, match="wrong revision"):
        launch.check_assessment(ROOT, ROOT / "assessment-version.json")


def test_uninitialized_assessment_dependency_is_rejected(monkeypatch):
    pin = json.loads((ROOT / "assessment-version.json").read_text())
    def output(argv, **kwargs):
        if "rev-parse" in argv:
            return pin["source_commit"] + "\n"
        return b"-abc evals\n" if "submodule" in argv else b""
    monkeypatch.setattr(launch.subprocess, "check_output", output)
    with pytest.raises(SystemExit, match="dependencies differ"):
        launch.check_assessment(ROOT, ROOT / "assessment-version.json")


@pytest.fixture
def fake_cli(tmp_path):
    cli = tmp_path / "fake-codex"
    cli.write_text(f"#!{sys.executable}\n" + '''
import json, os, pathlib, sys, tomllib
args = sys.argv[1:]
assert "CODEX_THREAD_ID" not in os.environ
if "debug" in args:
    config = next(x for x in args if x.startswith("skills.config="))
    for item in tomllib.loads(config)["skills"]["config"]:
        if item["enabled"]:
            print("- " + pathlib.Path(item["path"]).parent.name + ": fixture skill")
else:
    sys.stdin.read()
    pathlib.Path(args[args.index("-o") + 1]).write_text("Fixture report, not a live judgment.\\n")
    print(json.dumps({"type": "thread.started", "thread_id": "fake-test-session"}))
    print("fixture stderr", file=sys.stderr)
''')
    cli.chmod(0o755)
    profile = tmp_path / "profile"
    profile.mkdir()
    (profile / "config.toml").write_text("")
    return cli, profile


@pytest.mark.parametrize("role,condition,expected", [
    ("research", "baseline", set()),
    ("research", "skills", {
        "align-with-stamped-principles", "stamped-conventions", "create-stamped-project",
        "create-repronim-stamped-project", "do-full-research-loop", "pixi-with-stamped"}),
    ("judge", "baseline", {
        "assess-alignment-with-stamped-principles", "stamped-conventions"}),
])
def test_complete_fixture_launch_retains_evidence(tmp_path, fake_cli, role, condition, expected):
    cli, profile = fake_cli
    prompt = tmp_path / "prompt.txt"
    prompt.write_text("A fixed test prompt.\n")
    output = tmp_path / "evidence"
    environment = dict(os.environ, CODEX_HOME=str(profile), CODEX_THREAD_ID="must-be-removed")
    result = subprocess.run([
        sys.executable, str(ROOT / "scripts/launch_native_probe.py"),
        "--checkout", str(ROOT), "--prompt", str(prompt), "--output", str(output),
        "--cli", str(cli), "--role", role, "--condition", condition,
        "--review-seconds", "0"], env=environment, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    preflight = json.loads((output / "prompt-preflight.json").read_text())
    assert set(preflight["visible_study_skills"]) == expected
    record = json.loads((output / "result.json").read_text())
    assert record["timeout_seconds"] == 0
    assert record["timed_out"] is False
    assert record["native_session_ids"] == ["fake-test-session"]
    assert (output / "stderr.txt").read_text() == "fixture stderr\n"
    assert (output / "prompt.txt").read_bytes() == prompt.read_bytes()
    if role == "judge":
        assert record["condition"] is None
        assert record["assessment_pin"]["source_commit"]
        assert (output / "judgment").is_dir()
