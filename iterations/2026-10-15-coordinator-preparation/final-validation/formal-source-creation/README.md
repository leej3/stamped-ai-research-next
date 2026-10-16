# Formal source creation

These files preserve the existing formal repository construction evidence without rerunning either exporter.
The [export inventory](formal-root-export.json) records 56 source entries from `d0e616f1e9571a6701fe869858553c052b39eced` and the explicitly adapted paths.
The [tree verification](formal-source-tree-verification.json) records the comparison with formal commit `517d4d6957edf93e5f0e99dc3556393ce595f25e`, including the adapted study gitlink, new formal records, and absence of historical preparation iterations.

The [original exporter](export-formal-root.py) preserves its earlier source pin and original behavior.
The [refresh script](refresh-formal-root.py) preserves the later update procedure.
They are historical execution evidence, with their original absolute-context assumptions and failure behavior intact; they are not instructions to recreate the published repository.
The later receipt does not claim that the original exporter alone produced the final tree.

The [preservation manifest](../hosted-source-preservation.json) records byte hashes and source paths for all four files.
No procedure code, source repository, formal repository, or session was changed while preserving them.
