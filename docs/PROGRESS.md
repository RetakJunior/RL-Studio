# RL Studio progress

**Updated:** 2026-10-17

## Findings

- This is a Krita C++17/CMake source snapshot using Qt 5 by default, optional Qt 6, KDE Frameworks, and application/library/plugin/test directories.
- The source declares Krita 5.4.0-prealpha (Qt 5) or 6.1.0-prealpha (Qt 6).
- `rg --files -g '*.kra'` found 48 archives. Representative ZIP metadata was read without extracting or editing files; they are test fixtures, templates, and benchmark data, not an identified private RL Studio artwork pack.
- There is no `.git` metadata, so branch, remote, commit history, and clean/dirty state cannot be verified.
- CMake, Ninja, MSVC `cl`, and `msbuild` were initially unavailable on PATH. A separate supported LLVM MinGW/Qt/KDE environment has since been provisioned under `C:\rls-dev`.
- The Krita source tree was copied without exclusions to `C:\rls-dev\krita-source` (12,543 files, 547.47 MiB); the original workspace remains untouched by the build.
- CMake configure succeeded in `C:\rls-dev\b_krita` for Krita 5.4.0-prealpha using Qt 5, CMake 3.31.9, Clang 21.1.6, and KDE Frameworks 5.
- Full `ninja -j8 install` is currently building (5,093 planned Ninja steps; 674 completed at last check). Configure reported optional SIP/PyQt bindings and appstream test support unavailable; neither stopped configure.
- Clang identified a likely dangling reference in the existing Exiv2 0.28 path adapter (`KisExiv2IODevice::path()` returns a reference to a temporary string). Confirmed by reading the override signature and implementation; record it as a baseline defect and fix with a focused test after baseline build.
- Installed Krita 5.3.4.1 is separate from this source revision and is not a valid runtime baseline for it.
- The freehand benchmark source exists, but is registered as a broken test; runnable status is unknown.

## Work in this source tree

- Created/updated the requested project documents under `docs/` to describe a Krita-based downstream RL Studio direction and its current limits.
- No application source, asset, `.kra`, or upstream build file has been modified.

## Commands and outcomes

- `Get-ChildItem -Force`: confirmed source layout and missing `.git` directory.
- `rg --files -g '*.kra'`: 48 files; representative ZIP metadata inspected without extraction.
- Source review: CMake setup, application entry point, main window, canvas/input/rendering, resource, and test areas.
- Portable Git `status`/`rev-parse`: failed because this directory is not a Git work tree.
- Toolchain probes: CMake, Ninja, MSVC `cl`, and `msbuild` unavailable on PATH.
- Build: running; no compile error so far. Existing compiler warnings include the Exiv2 path lifetime issue plus enum/unused-parameter diagnostics.
- Tests, benchmark, and source-version UI workflow: not run yet.

## Next actions

1. Recover the correct Git checkout/history or make a protected copy before importing this snapshot; do not overwrite source files.
2. Finish the out-of-source build and record final warnings/errors.
3. Establish source-matched app, test, UI, and freehand performance baselines.
4. Implement and validate a narrow RL Studio product change.
5. Review GPL and third-party license obligations before downstream distribution.
