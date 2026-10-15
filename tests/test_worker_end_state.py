"""Worker-stop evidence and attribution checks using only local Git fixtures."""
import base64
import errno
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import launch_native_probe as launch
import worker_end_state as state


def git(path, *args):
    return subprocess.check_output(["git", "-C", str(path), *map(str, args)]).strip()


def init(path):
    path.mkdir()
    git(path, "init", "-b", "main")
    git(path, "config", "user.name", "Worker receipt fixture")
    git(path, "config", "user.email", "fixture@example.invalid")
    git(path, "config", "core.hooksPath", path / ".git/empty-hooks")
    (path / "tracked.txt").write_text("Original scientific input\n")
    (path / ".gitignore").write_text(".pixi/\nignored/\n")
    commit(path)
    return path


def commit(path):
    git(path, "add", "--all")
    git(path, "commit", "-m", "test: retain synthetic fixture")
    return git(path, "rev-parse", "HEAD").decode()


def rows(receipt):
    return {item["path"]: item for item in receipt["worktree"]}


def test_capture_separates_index_worktree_and_untracked_without_mutation(tmp_path):
    repo = init(tmp_path / "worker")
    head = git(repo, "rev-parse", "HEAD").decode()
    (repo / "tracked.txt").write_text("Staged result\n")
    git(repo, "add", "tracked.txt")
    (repo / "tracked.txt").write_text("Actual final result\n")
    odd = "output with\nnewline\tand tab.txt"
    (repo / odd).write_bytes(b"new result")
    (repo / ".pixi").mkdir()
    os.mkfifo(repo / ".pixi/do-not-read")
    (repo / "ignored").mkdir()
    (repo / "ignored/cache.bin").write_bytes(b"not inventoried")
    (repo / "ignored/tracked.bin").write_bytes(b"explicitly tracked")
    git(repo, "add", "-f", "ignored/tracked.bin")
    index = repo / ".git/index"
    before = (index.read_bytes(), index.stat().st_mtime_ns)
    receipt = state.capture_worker_end_state(repo)
    assert receipt["capture_status"] == "complete", receipt["errors"]
    assert receipt["head_commit"] == head
    assert receipt["captured_at"] <= receipt["capture_finished_at"]
    assert base64.b64decode(receipt["status_porcelain_v1_z_base64"]) == subprocess.check_output([
        "git", "--no-optional-locks", "-C", str(repo), "status", "--porcelain=v1", "-z",
        "--untracked-files=all", "--ignore-submodules=none"])
    observed = rows(receipt)
    assert observed["tracked.txt"]["sha256"] == hashlib.sha256(b"Actual final result\n").hexdigest()
    assert observed[odd]["tracked"] is False
    assert observed["ignored/tracked.bin"]["tracked"] is True
    assert not any(path.startswith(".pixi/") for path in observed)
    assert "ignored/cache.bin" not in observed
    assert (index.read_bytes(), index.stat().st_mtime_ns) == before
    assert git(repo, "rev-parse", "HEAD").decode() == head


def test_symlinks_record_targets_without_reading_external_contents(tmp_path):
    repo = init(tmp_path / "worker")
    outside = tmp_path / "external"
    outside.mkdir()
    os.mkfifo(outside / "would-hang")
    (repo / "link").symlink_to(outside / "would-hang")
    (repo / "directory-link").symlink_to(outside, target_is_directory=True)
    (repo / "broken").symlink_to("absent")
    receipt = state.capture_worker_end_state(repo)
    assert receipt["capture_status"] == "complete"
    for name in ("link", "directory-link", "broken"):
        row = rows(receipt)[name]
        target = os.readlink(os.fsencode(repo / name))
        assert row["kind"] == "symlink"
        assert row["sha256"] == hashlib.sha256(target).hexdigest()
        assert row["link_target"] == os.fsdecode(target)


def test_changed_parent_symlink_cannot_redirect_tracked_file_reads(tmp_path):
    repo = init(tmp_path / "worker")
    (repo / "data").mkdir()
    (repo / "data/input.txt").write_text("input")
    commit(repo)
    (repo / "data/input.txt").unlink()
    (repo / "data").rmdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    os.mkfifo(outside / "input.txt")
    (repo / "data").symlink_to(outside, target_is_directory=True)
    receipt = state.capture_worker_end_state(repo)
    assert receipt["capture_status"] == "partial"
    assert any("parent component" in error["error"] for error in receipt["errors"])


def test_non_utf8_filename_round_trips_in_receipt(tmp_path):
    repo = init(tmp_path / "worker")
    name = b"output-\xff.txt"
    try:
        with open(os.fsencode(repo) + b"/" + name, "wb") as stream:
            stream.write(b"output")
    except OSError as exc:
        if exc.errno == errno.EILSEQ:
            pytest.skip("Host filesystem rejects non-UTF-8 filenames")
        raise
    receipt = json.loads(json.dumps(state.capture_worker_end_state(repo)))
    assert receipt["capture_status"] == "complete"
    assert rows(receipt)[os.fsdecode(name)]["sha256"] == hashlib.sha256(b"output").hexdigest()


def test_missing_tracked_and_special_file_leave_partial_evidence(tmp_path):
    repo = init(tmp_path / "worker")
    (repo / "unexpected-pipe").write_text("was a regular tracked file")
    commit(repo)
    (repo / "tracked.txt").unlink()
    (repo / "unexpected-pipe").unlink()
    os.mkfifo(repo / "unexpected-pipe")
    receipt = state.capture_worker_end_state(repo)
    assert rows(receipt)["tracked.txt"]["kind"] == "missing"
    assert receipt["head_commit"]
    assert receipt["capture_status"] == "partial"
    assert any("special file" in error["error"] for error in receipt["errors"])


def test_repository_loss_does_not_capture_parent_repository(tmp_path):
    parent = init(tmp_path / "parent")
    missing = parent / "lost-repository"
    missing.mkdir()
    receipt = state.capture_worker_end_state(missing)
    assert receipt["capture_status"] == "partial"
    assert receipt["head_commit"] is None
    assert any(error["operation"] == "repository boundary" for error in receipt["errors"])


def test_submodules_and_untracked_embedded_repositories_are_inventoried(tmp_path):
    source = init(tmp_path / "source")
    repo = init(tmp_path / "worker")
    git(repo, "-c", "protocol.file.allow=always", "submodule", "add", source, "module")
    commit(repo)
    (repo / "module/observations.txt").write_bytes(b"uncommitted submodule output")
    embedded = init(repo / "embedded")
    (embedded / "result.txt").write_text("new nested output")
    receipt = state.capture_worker_end_state(repo)
    assert receipt["capture_status"] == "complete", receipt["errors"]
    module = receipt["submodules"][0]
    assert module["initialized"] is True
    assert module["index_commit"] == git(source, "rev-parse", "HEAD").decode()
    assert rows(module["repository"])["observations.txt"]["tracked"] is False
    assert rows(receipt["embedded_repositories"][0]["repository"])["result.txt"]["tracked"] is False
    git(repo, "submodule", "deinit", "--force", "module")
    receipt = state.capture_worker_end_state(repo)
    assert receipt["capture_status"] == "complete", receipt["errors"]
    assert receipt["submodules"][0]["initialized"] is False


def test_receipt_retention_and_validation_do_not_grant_worker_commit_credit(tmp_path):
    repo = init(tmp_path / "worker")
    head = git(repo, "rev-parse", "HEAD").decode()
    (repo / "result.txt").write_bytes(b"scientific output")
    output = tmp_path / "evidence"
    output.mkdir()
    pointer = state.save_worker_end_state(repo, output, {"returncode": 0, "stop_reason": "exited"})
    content = (output / pointer["path"]).read_bytes()
    assert pointer["sha256"] == hashlib.sha256(content).hexdigest()
    receipt = json.loads(content)
    assert receipt["head_commit"] == head
    assert rows(receipt)["result.txt"]["tracked"] is False
    preserved = commit(repo)
    result = state.validate_retained_artifacts(receipt, repo)
    assert result == {"worker_head_commit": head, "result_commit": preserved, "artifacts_match": True}
    assert head != preserved
    (repo / "result.txt").write_bytes(b"coordinator altered result")
    commit(repo)
    with pytest.raises(ValueError, match="artifacts differ"):
        state.validate_retained_artifacts(receipt, repo)
    assert (output / pointer["path"]).read_bytes() == content
    with pytest.raises(ValueError, match="outside"):
        state.save_worker_end_state(repo, repo, {})


def test_annex_preservation_compares_available_bytes_and_retains_link_semantics(tmp_path):
    repo = init(tmp_path / "worker")
    (repo / "result.bin").write_bytes(b"payload preserved without changes")
    receipt = state.capture_worker_end_state(repo)
    key = "SHA256E-s33--fixture.bin"
    obj = repo / ".git/annex/objects/ab/cd" / key / key
    obj.parent.mkdir(parents=True)
    (repo / "result.bin").rename(obj)
    target = str(obj.relative_to(repo))
    (repo / "result.bin").symlink_to(target)
    commit(repo)
    captured = state.capture_worker_end_state(repo)
    row = rows(captured)["result.bin"]
    assert row["kind"] == "symlink"
    assert row["link_target"] == target
    assert row["annex_key"] == key
    assert row["annex_content"]["sha256"] == hashlib.sha256(obj.read_bytes()).hexdigest()
    assert state.validate_retained_artifacts(receipt, repo)["artifacts_match"] is True
    obj.write_bytes(b"different payload despite unchanged pointer")
    with pytest.raises(ValueError, match="artifacts differ"):
        state.validate_retained_artifacts(receipt, repo)


@pytest.mark.parametrize("exit_code,timeout", [(0, False), (7, False), (0, True)])
def test_failed_and_timed_out_workers_keep_stop_receipt(tmp_path, monkeypatch, exit_code, timeout):
    repo = init(tmp_path / "worker")
    output = tmp_path / "evidence"
    output.mkdir()
    monkeypatch.setattr(launch.time, "sleep", lambda _: None)
    program = ("import pathlib,sys,time; sys.stdin.read(); "
               "pathlib.Path('result.txt').write_text('worker output'); "
               + ("time.sleep(60)" if timeout else f"sys.exit({exit_code})"))
    process = subprocess.Popen([sys.executable, "-c", program], cwd=repo,
                               stdin=subprocess.PIPE, process_group=0)
    record = {}
    try:
        assert launch.wait_and_capture_worker(process, b"fixture", output, repo, record,
                                              "research", .2 if timeout else 0, 0) == timeout
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
    receipt = json.loads((output / "worker-end-state.json").read_text())
    assert receipt["worker"]["timed_out"] == timeout
    assert receipt["worker"]["returncode"] == process.returncode
    assert receipt["worker"]["stop_reason"] == ("timeout" if timeout else "exited")
    assert rows(receipt)["result.txt"]["tracked"] is False
    assert receipt["worker"]["stopped_at"] <= receipt["captured_at"]
    assert json.loads((output / "result.json").read_text())["worker_end_state"] == record["worker_end_state"]


def test_early_exit_before_reading_prompt_still_retains_receipt(tmp_path):
    repo = init(tmp_path / "worker")
    output = tmp_path / "evidence"
    output.mkdir()
    process = subprocess.Popen([sys.executable, "-c", "raise SystemExit(9)"],
                               stdin=subprocess.PIPE, process_group=0)
    process.wait()
    launch.wait_and_capture_worker(process, b"x" * 65536, output, repo, {}, "research", 0, 0)
    assert json.loads((output / "worker-end-state.json").read_text())["worker"]["returncode"] == 9


def test_partial_receipts_are_rejected_for_formal_artifact_validation(tmp_path):
    repo = init(tmp_path / "worker")
    receipt = state.capture_worker_end_state(repo)
    receipt["capture_status"] = "partial"
    with pytest.raises(ValueError, match="incomplete"):
        state.validate_retained_artifacts(receipt, repo)


def test_preservation_must_retain_original_worker_history(tmp_path):
    repo = init(tmp_path / "worker")
    receipt = state.capture_worker_end_state(repo)
    git(repo, "checkout", "--orphan", "rewritten-preservation")
    git(repo, "commit", "-m", "test: create unrelated preservation history")
    with pytest.raises(ValueError, match="worker HEAD"):
        state.validate_retained_artifacts(receipt, repo)


def test_clean_submodule_identity_does_not_require_initialization(tmp_path):
    source = init(tmp_path / "source")
    repo = init(tmp_path / "worker")
    git(repo, "-c", "protocol.file.allow=always", "submodule", "add", source, "module")
    commit(repo)
    receipt = state.capture_worker_end_state(repo)
    git(repo, "submodule", "deinit", "--force", "module")
    report = state.validate_retained_artifacts(receipt, repo)
    assert report["submodule_identity_without_checkout"] == ["module"]
    git(repo, "-c", "protocol.file.allow=always", "submodule", "update", "--init")
    (repo / "module/new-result.txt").write_text("uncommitted result")
    dirty = state.capture_worker_end_state(repo)
    git(repo, "submodule", "deinit", "--force", "module")
    with pytest.raises(ValueError, match="artifacts differ"):
        state.validate_retained_artifacts(dirty, repo)


def test_sha256_annex_identity_without_payload_is_explicit_and_checks_size(tmp_path):
    repo = init(tmp_path / "worker")
    payload = b"scientific output preserved in annex"
    (repo / "result.bin").write_bytes(payload)
    receipt = state.capture_worker_end_state(repo)
    digest = hashlib.sha256(payload).hexdigest()
    key = f"SHA256E-s{len(payload)}--{digest}.bin"
    (repo / "result.bin").unlink()
    (repo / "result.bin").symlink_to(f".git/annex/objects/ab/cd/{key}/{key}")
    commit(repo)
    report = state.validate_retained_artifacts(receipt, repo)
    assert report["annex_identity_without_local_payload"] == ["result.bin"]
    wrong_key = f"SHA256E-s999--{digest}.bin"
    (repo / "result.bin").unlink()
    (repo / "result.bin").symlink_to(f".git/annex/objects/ab/cd/{wrong_key}/{wrong_key}")
    commit(repo)
    with pytest.raises(ValueError, match="artifacts differ"):
        state.validate_retained_artifacts(receipt, repo)


def test_interrupt_retains_receipt_before_propagating(tmp_path, monkeypatch):
    repo = init(tmp_path / "worker")
    output = tmp_path / "evidence"
    output.mkdir()
    process = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"],
                               stdin=subprocess.PIPE, process_group=0)
    monkeypatch.setattr(launch.time, "sleep", lambda _: None)
    def interrupt(*args):
        raise KeyboardInterrupt()
    monkeypatch.setattr(launch, "wait_for_worker", interrupt)
    with pytest.raises(KeyboardInterrupt):
        launch.wait_and_capture_worker(process, b"fixture", output, repo, {}, "research", 0, 0)
    assert process.poll() is not None
    assert json.loads((output / "worker-end-state.json").read_text())["worker"]["stop_reason"] == "launcher-interrupted"
