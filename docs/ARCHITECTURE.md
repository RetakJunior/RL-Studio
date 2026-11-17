# Source architecture

## Observed foundation

The workspace is a large C++17 desktop application using CMake, Qt Widgets, KDE Frameworks, and a plugin/library architecture. Qt 5 is the default; Qt 6 is optional. The root CMake declares Krita 5.4.0-prealpha or 6.1.0-prealpha depending on the Qt path.

- `krita/`: application entry point, metadata, shell resources, integration, and packaging.
- `libs/image/`, `libs/command/`: image storage, color spaces, tiled data, and undoable commands.
- `libs/ui/`: document/view lifecycle, canvas, input, actions, dialogs, and application UI.
- `libs/brush/`, `plugins/paintops/`: brush resources, engines, and paint operations.
- `plugins/dockers/`: dockable workspace panels.
- `libs/*/tests`, `plugins/*/tests`, `benchmarks/`: focused tests and workloads.
- `krita/data/`, `pics/`: application resources; provenance and redistribution terms need review before downstream packaging.

## Downstream boundary

Start RL Studio as a narrow downstream layer over this architecture. Preserve internal identifiers and user data paths until migration and parallel-installation behavior are designed. Separate user-facing branding from compatibility identifiers. Avoid broad replacements of `Krita` symbols, plugin IDs, resource paths, translations, or file formats.

## Change workflow

Map a behavior to its existing owner, make the smallest change there, locate its closest tests, then build/test in a disposable out-of-source directory. UI work needs a real interaction review; performance work needs a repeatable before/after benchmark.
