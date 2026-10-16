# Hosted checkpoint claim recheck

The independent hosted metadata recheck matched all 15 expected checkpoint and session identities: six setup checkpoints and six research checkpoints from the original `stamped-ai-research` pilot, plus three preparation checkpoints from `stamped-ai-research-next`.
The [summary](summary.json) and [expected identities](expected.json) identify the complete set and its original receipt sources.

Each query used Entire CLI 0.11.4 from a freshly initialized Git repository with no objects, refs, remotes, HEAD commit, alternates, or local Entire data.
All inherited `GIT_*` environment variables were removed.
Before and after Git state matched for every query, excluding the matching-checkout fallback that made earlier `--repo` checks ambiguous.
Each checkpoint directory retains `commands.json`, raw stdout and stderr, their SHA-256 hashes, and `result.json`.
The [audit script](recheck.py) is retained as executed; its absolute paths describe the original host and are not a portable replay interface.

The [evidence URL index](evidence-urls.json) contains twelve immutable GitHub receipt URLs.
All twelve raw-URL requests returned HTTP 200, and their byte hashes matched both the original local receipts and their committed Git blobs.
The index retains request URLs, status, and computed hashes; HTTP response bodies and headers were not saved.
These URLs locate the original identity evidence; the hosted query results are retained separately here.
Entire's metadata did not return checkpoint dashboard URLs, so no such URLs were inferred.

This audit establishes hosted metadata identity and receipt availability.
It does not verify hosted raw transcript contents, visually inspect the dashboard, reassess scientific results, or establish new native capture.
No sessions, uploads, or onboarding were performed for this audit.

The [preservation manifest](../hosted-source-preservation.json) records unchanged source-file hashes.
The original empty Git contexts remain outside the repository; their complete command and state receipts are retained here.
[Formal source-creation evidence](../formal-source-creation/README.md) is preserved separately.
