# Remote delivery checks

The annex probe contains public deterministic bytes, not credentials.
Its complete upload record is retained in `logs/annex-upload-001/`.
The CON Hub repository is the annex destination; GitHub hosts Git history.

`logs/cluster-environment-001/` preserves an initial failed cluster environment attempt.
A shell startup message had broken the preceding file transfer, so the manifest was absent.
The corrected batch-job trial is in `experiments/cluster/`.

Personal authentication remains in host credential providers.
Cluster results return through the local host for online publication.

An independent clone fetched the probe, numerical table and PNG from CON Hub with credential helpers and interactive prompts disabled.
All three SHA-256 hashes matched.
See [receipt](remote-retrieval.json) and the complete `logs/annex-recipient-001/` record.
