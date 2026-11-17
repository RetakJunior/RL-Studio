# RL Studio repository audit

**Audit date:** 2026-10-17 (client local date)  
**Status:** static inspection complete; runnable baseline unavailable in this environment.

## Executive finding

The workspace is a large Krita source tree, not a pre-existing RL Studio application or a small Krita-based prototype. Its root `CMakeLists.txt`, `README.md`, `krita/`, `libs/`, `plugins/`, `pics/`, and `3rdparty*` layout identify it as Krita. The source declares a pre-release Krita 5.4 or 6.1 version depending on the Qt build selection. RL Studio does not yet exist as a distinct product in the inspected tree.

The source already contains mature painting, document, layer, undo, input-profile, canvas-rendering, resource, and test subsystems. The product direction is a Krita-based downstream RL Studio fork. Replacing the engine or broadly rebranding the tree before a reproducible source build and package/compatibility plan would be high risk. Preserve upstream identity and licensing details until an integrated brand/package plan can be validated.

## Repository and environment

| Check | Finding |
|---|---|
| Workspace root | `C:\Users\Retak\Documents\Projects\RL Studio wiin` |
| Root project | Krita CMake/C++ source tree |
| Git metadata | No `.git` directory present; branch, commit history, status, and remote cannot be read |
| Git executable | Not available on PATH |
| Build tools | `cmake`, `ninja`, MSVC `cl`, and `msbuild` are not available on PATH |
| Krita executable | Not available on PATH; a separate installed `C:\Program Files\Krita (x64)\bin\krita.exe` is present (Windows version metadata: Krita 5.3.4.1, git `bd6e8d0`) |
| Python | WindowsApps shim is present; a usable interpreter was not established |
| Build directories | No root build/output directory found |
| Existing RL Studio app/docs | No app-specific source or pre-existing `docs/` tree found during initial inspection |

No files were modified before these checks. The source snapshot cannot be assumed clean or tied to any remote. Do not claim a branch, commit, remote, clean status, successful build, successful test run, or release state until the needed metadata/tooling is provided and checked.

## Technology and project structure

- C++ desktop application using CMake, Qt Widgets, KDE Frameworks, and a large plugin/library architecture.
- Qt 5 is the default build path in the root CMake file; Qt 6 is an option. The selected path affects the declared pre-release version (5.4.0-prealpha or 6.1.0-prealpha).
- Top-level areas include `krita/` (application shell/data), `libs/` (shared application, image, brush, color, document, undo, and UI infrastructure), `plugins/` (paint operations, tools, filters, dockers, import/export, generators, color engines), `qmlmodules/`, `3rdparty/`, `3rdparty_vendor/`, `3rdparty_plugins/`, `packaging/`, `sdk/`, and `benchmarks/`.
- `README.md` points contributors to Krita's upstream build documentation. The root `CMakeLists.txt` performs extensive required and optional dependency discovery; the complete dependency set was not resolved in this environment.
- The tree contains CI configuration (`.gitlab-ci.yml`, `.kde-ci.yml`, `.github/`) and CMake test targets, but no CI result or build artifact was inspected.

## Product subsystem map

| Concern | Observed source areas | Audit interpretation |
|---|---|---|
| Application shell/actions | `krita/main.cc`, `krita/krita5.xmlgui`, `libs/ui/KisMainWindow.*`, `libs/ui/actions/` | Existing action manager and XMLGUI-based menu/action definitions are established extension points. This is not a blank menu shell. |
| Documents | `libs/ui/KisDocument.*`, `libs/ui/KisView.*`, `plugins/impex/libkra/` | Native document lifecycle and `.kra` I/O already exist. Opening/saving behavior needs runtime tests before any reliability claim. |
| Image/layers/undo | `libs/image/`, `libs/command/`, `libs/image/tiles3/` | Mature tiled image and command/undo infrastructure exists; reuse it. |
| Input/tablet | `libs/ui/input/`, including `kis_input_manager.*`, `kis_tablet_debugger.*`, WinTab tester and tablet dialogs | Mouse, tablet, touch/navigation shortcuts and configurable input profiles are present. Actual device behavior cannot be verified here. |
| Brush/stroke | `libs/brush/`, `libs/image/brushengine/`, `plugins/paintops/`, `libs/ui/tool/strokes/` | Brush engines and freehand stroke code are separate layers. `FreehandStrokeBenchmark` exists as a candidate baseline, but could not be run. |
| Canvas presentation | `libs/ui/canvas/`, `libs/ui/opengl/` | Canvas widgets and OpenGL texture/tile paths exist, including LoD/dirty texture handling. Presence of GPU code is not evidence of a given device's performance or fallback behavior. |
| Panels/workspace | `plugins/dockers/`, `libs/ui/KisMainWindow.*` | Dockers and workspace behavior are already implemented. Keep any new UI consistent with these conventions. |
| Assets | `krita/data/`, `pics/`, plugin resources | Assets are primarily source-tree application data and icons, not a user-supplied RL Studio brush pack. |
| Tests/benchmarks | `libs/*/tests`, `plugins/*/tests`, `benchmarks/`, `libs/ui/tests/FreehandStrokeBenchmark.*` | Many focused CMake tests and sample files exist. Test discovery is not equivalent to executing them. |

## Krita file inventory

`rg --files -g '*.kra'` returned 48 files. Archive contents were readable with the .NET ZIP reader and representative `maindoc.xml` metadata was inspected without extracting or modifying files. These `.kra` files are a mixture of:

- bundled new-document templates: texture (including 4K/8K and scalar formats), DSLR/photo, design, comics, and animation;
- automated test fixtures under `libs/` and import/export plugins;
- a benchmark loading fixture (`benchmarks/data/load_test.kra`);
- a gamut-mask template.

Examples confirmed by archive metadata include a 1000×753 RGBA loading fixture, a 494×774 RGBA16 flood-fill fixture, a 1920×1080 animation fixture, 512×512 RGBAF32 and 512×215 RGBAF32 HDR fixtures, 512×512 CMYK/JXL fixtures, and 8162×8162 RGBA / 8192×8192 GRAYAF32 texture templates. Test assets include ordinary, animation, HDR, CMYK, proofing, and multilayer cases. These are functional Krita fixtures/templates, not evidence of a private RL Studio artwork collection. The archive headers are readable; visual output and layer semantics have not been inspected in the running application.

`krita/data/` alone contains 178 PNG, 110 ICC, 78 PAT, 33 KRA, 24 predefined-image, 17 GGR, 16 KPP, 13 GPL, 9 palette/color, and other resource files (grouped by extension; directory is about 83 MB). Brush/preset/palette resources must be inventoried with their upstream licenses and intended redistribution terms before bundling them under a new product identity.

## Licensing and upstream obligations

The root `COPYING` is GNU GPL version 3. The tree includes `LICENSES/` notices and many third-party components with distinct licenses. This audit does not establish the license of every file or prove rights to rebrand and redistribute the tree. A downstream RL Studio distribution based on this code needs a file-level license/notice review, source and attribution compliance, dependency notices, and a clear distinction between upstream Krita code/assets and original RL Studio work. Keep notices and provenance intact; get legal review before a public distribution or brand claim.

## Baseline and limits

- **Build:** CMake configure succeeded from a protected, no-space copy at `C:\rls-dev\krita-source` into `C:\rls-dev\b_krita` using CMake 3.31.9, Clang 21.1.6/LLVM MinGW, Qt 5, and KDE Frameworks 5. Full `ninja -j8 install` is in progress; configure alone does not establish build success.
- **Application launch/UI workflows:** a `--version` CLI smoke probe against the separately installed Krita executable did not exit within 10 seconds and was stopped. No UI workflow was verified. The installed version is 5.3.4.1 (`bd6e8d0`); it is not a build of this source snapshot (which declares 5.4.0-prealpha by default or 6.1.0-prealpha with Qt 6), so it cannot serve as this tree's runtime baseline.
- **Automated tests/benchmarks:** not run yet; the configured build has not produced test binaries. The freehand benchmark still needs a manual run check after the build.
- **Git baseline:** unavailable: both `.git` metadata and the `git` executable are absent.
- **Performance:** no numbers collected. No performance improvement is claimed.
- **Source test inventory:** source-level discovery confirms tests and a freehand benchmark exist; their actual pass/fail state remains unknown. In `libs/ui/tests/CMakeLists.txt`, the freehand benchmark uses `krita_add_broken_unit_test`, so its availability/executability must be resolved in a configured build before treating it as a usable benchmark.

## Immediate risks and next action

1. Recover/initialize the intended `Rl-Studio-wiin` Git repository without overwriting this source snapshot or losing user changes.
2. Finish the configured source build, launch the resulting baseline, and run representative tests/benchmark if the targets are produced.
3. Resolve Git history/remote without overwriting this source snapshot, then define parallel-installation, settings migration, package identity, and brand/license handling.
4. After baseline, implement one narrow user-facing improvement with tests and UI evidence; performance work must include comparable measurements.

See [technical decisions](TECHNICAL_DECISIONS.md), [roadmap](IMPLEMENTATION_ROADMAP.md), and [progress](PROGRESS.md).
