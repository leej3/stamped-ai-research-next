# Tiny Slurm transfer and compute proof

This module transfers the root manifest, exact ignored lock, and the five-value SciPy fixture to Unity.
It installs the locked Linux environment, submits one CPU job, and retrieves scheduler output, accounting, complete remote duct records and generated artifacts.
The local NumPy/pandas comparison and independent known-answer oracle must both pass.
Numerical agreement is the cross-platform requirement; image bytes may differ across platforms.

From a prepared repository root with the validated local fixture outputs present:

```sh
pixi run --locked duct -p experiments/cluster/logs/toy-001/run_ \
  --fail-time 0 --capture-outputs all --outputs all --record-types all \
  python experiments/cluster/trial.py --run-id toy-001 --source "$PWD"
```

Use a new run ID for another attempt.
The runner requires working SSH, the configured Slurm account and partition, a writable remote parent directory, and the remote Pixi executable.
Its `--help` exposes the host-specific defaults.
It refuses different local/source bytes and preserves individual command streams and failure status in `receipts/<run-id>/`.
The recorded lock must remain unchanged; a version incompatibility is a blocker to diagnose, not permission to solve a different environment.
The job requests one CPU, 2 GiB and five minutes of runtime; installation and queue waits are separate and have no five-minute completion guarantee.

The initial SCP transport failure came from a diagnostic printed by the remote noninteractive shell.
The explicitly authorized one-time `repair_ssh_startup.py` changed only the exact fourth-line diagnostic to an interactive-shell condition and retained a backup on that host.
Its capture records hashes and the backup location, without copying the shell configuration into this repository.
The repair script deliberately rejects an already-changed or unexpected file.

This proof uses selected transferred files and a locally relayed result.
It does not establish a full Git/submodule reconstruction, cluster DataLad replay, online annex transfer, native cluster conversation capture, or scientific efficacy.

The first run, `toy-001`, passed on Unity job `65719918` (`uri-cpu100`), with scheduler state `COMPLETED` and exit `0:0`.
Pixi 0.73.0 installed the unchanged recorded lock in 173.350 seconds.
Slurm reported 14 seconds of job elapsed time and batch MaxRSS of 311216 KiB; the remote duct computation took 8.223 seconds with peak RSS 162.4 MB.
The complete local orchestration took 226.804 seconds, including transfer, installation, scheduler observation and retrieval.
The independent numerical oracle and local table comparison passed, and all three returned artifact hashes also matched the local run.
The lock SHA-256 remained `a4ae3328c4df725aeb2529c0b25d43e0ad5f57fc5ec7c7eb6b82d45806a626ef`.
These timings describe this run; they are not queue or installation guarantees.
