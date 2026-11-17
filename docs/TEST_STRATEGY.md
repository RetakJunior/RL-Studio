# Test strategy

## Current inventory

The tree contains CMake test targets under `libs/` and `plugins/`. The freehand benchmark is in `libs/ui/tests/`, but is registered as a broken test in the inspected CMake file. No tests have run against this snapshot because no configured build or required C++/Qt/KDE toolchain is available.

## Baseline checks

- Configure/build supported targets in an out-of-source directory.
- Run focused document open/save, image/layer/undo, input, canvas, and plugin tests.
- Launch the built executable and verify open, draw, undo/redo, save/reopen, and PNG export.
- Record commands, test names, configuration, and failures.
- Establish a repeatable freehand workload; discovering a test file is not a passing test.

## New-change requirements

- Add/extend focused tests for behavior changes.
- Preserve fixtures and user artwork.
- For UI changes, record manual workflows and screenshots at representative scales.
- For performance changes, compare matching builds with repeated runs.
- Review licenses for bundled asset or package changes.
