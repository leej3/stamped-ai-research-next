# Cold public recipient replay

An independent agent cloned the published GitHub repository at `0cc86e8`, initialized its skills submodule, retrieved the separate environment snapshot, and followed the published DataLad guidance using stable recipient-side helpers.

Attempt 001 failed because switching the parent to the historical base did not update the already installed skills submodule.
Its complete evidence remains in `../recipient-cold-001/`.
The instructions and reusable DataLad skill now require `git submodule update --init --recursive` after that checkout.

With that explicit correction, attempt 002 passed 15 checks across 28 subprocesses in 46.525 seconds.
Outputs and annex payloads started absent.
The independent numerical oracle and all three original output hashes matched; native replay failed with “No run commits found”; a zero-exit no-op failed the same verifier.
The PNG was visually inspected.

See [summary](receipts/summary.json), [artifact audit](audit.json), retained driver and complete `logs/` records.
Replay commit `2e8b7449219345490791badd87184ed7d5ec2b00` is retained on `codex/proof-recipient-cold`.
No published implementation was changed inside these trials; the setup correction is an explicit intervention.
