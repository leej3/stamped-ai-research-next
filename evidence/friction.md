# Instruction friction observed during completion

The copied DataLad stack states: "datalad, datalad-container, git-annex (its
PyPI wheel ships a standalone build) and con-duct install from PyPI".
On this host the first Pixi solve failed because its implicit macOS target was
13 while the git-annex wheel required 14.
The initial error and intervention are retained in
`setup/pypi-git-annex-failure.txt`.
Declaring macOS >=14 allowed the dependency install.
Pixi's legacy `[system-requirements]` route worked but warned it was deprecated;
its suggested custom-platform route needed a name different from the `osx-arm64`
subdir.
The rejected platform declaration is retained in
`setup/platform-name-failure.txt`.

The stack recommends "datalad create -c text2git when the text files may be
shared publicly".
That command created the dataset, then its text2git procedure failed because the
declared git-annex wheel lacks MagicMime and cannot parse `mimeencoding`.
A bounded diagnostic reproduction is saved verbatim in
`setup/text2git-failure.txt`.
The workaround was explicit path-based rules:
source/specification files in Git, results/logs in annex, lock snapshots in Git.

The stack says to "keep logs and scratch output outside the dataset" while the
selected research-loop and Pixi skills explicitly require requested logs "with
the owning experiment".
I interpreted the former as transient setup/scratch guidance and retained the
requested completed logs inside a declared DataLad output path, which permits
clean-input recorded execution.

The user requested a single tiny known-answer trial.
A separate narrative-guided scientific reviewer was waived by the task
coordinator in favor of independently expressed rational-arithmetic expected
values and a second SciPy paired-test route.
The STAMPED assessment still runs separately against the committed object.
