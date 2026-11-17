# RL Studio

RL Studio is a cross-platform digital painting application based on the Krita source tree. It keeps Krita's document formats, plugins, and compatible internal identifiers while presenting the RL Studio name and visual identity to users.

![RL Studio](logos/RL%20Studio.png)

## Downloads

Release packages are published on the [GitHub Releases page](https://github.com/RetakJunior/RL-Studio/releases). Linux builds are distributed as AppImages; Windows and macOS packages are attached when a tagged release build completes.

## Build from source

This is a large Qt/KDE application. Use the platform-specific setup documented in the [Krita build guide](https://docs.krita.org/en/untranslatable_pages/building_krita.html). Linux AppImage packaging uses the [official Docker build environment](https://docs.krita.org/en/untranslatable_pages/building/build_krita_with_docker_on_linux.html).

GitHub Actions will build packages from this repository. Open the repository's **Actions** tab to view build runs and their downloadable artifacts.

## Project files and compatibility

RL Studio retains Krita's native `.kra` project format and the compatible plugin API. Krita's internal identifiers remain where they are required to read existing documents, support plugins, or load file format handlers.

## License

RL Studio is based on Krita and KDE components. The source tree's license files and per-file notices govern redistribution; the main application is distributed under GPL-3.0-or-later. See [COPYING](COPYING) and [LICENSES](LICENSES).
