# Implementation roadmap

## Stage 0: source audit — documented

- Confirm the workspace is a Krita C++/Qt source snapshot and map its major painting subsystems.
- Record environment, test/benchmark, asset, and license constraints.
- Avoid broad branding edits before a reproducible fork build exists.

## Stage 1: recover a baseline — next

- Recover the intended Git checkout/history and verify branch/remotes without overwriting this snapshot.
- Provision supported Windows build dependencies and configure out-of-source.
- Build, launch, run selected tests, and establish a repeatable freehand workload or document why the existing target cannot run.
- Capture a basic UI workflow and distinguish baseline failures from later regressions.

## Stage 2: product foundation

- Define RL Studio branding/package identity while preserving internal IDs and user-data compatibility.
- Review inherited and original icons, splash assets, translations, licenses, and credits.
- Implement a narrow user-visible improvement with tests and UI evidence.

## Stage 3: measured product work

- Select workflow or stroke/render improvements from user needs and baseline measurements.
- Add focused tests and before/after evidence.
- Expand installer/release work after license, build, and migration checks.

Later stages are plans, not implemented features or release-date commitments.
