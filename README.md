# RL Studio

A lightweight, high-performance desktop painting and concept art studio for Linux.

Built on Qt5 and packaged as a portable AppImage.

![RL Studio Splash](logos/RL%20Studio.png)

## Installation

### AppImage (Recommended)

Download the latest standalone AppImage from [Releases](https://github.com/RetakJunior/RL-Studio/releases):

```bash
chmod +x RLStudio-x86_64.AppImage
./RLStudio-x86_64.AppImage
```

No dependencies or system installation needed.

### PyPI

You can also install the runner via pip:

```bash
pip install --upgrade rlstudio
rlstudio
```

## Supported File Formats

- **Native Format**: `.rls` (RL Studio project format, backward-compatible with `.kra`)
- **Vector & Icons**: `.svg`, `.ico`
- **Raster Formats**: `.png`, `.jpg`, `.jpeg`, `.webp`, `.tga`, `.tiff`, `.bmp`, `.psd`, `.exr`, `.gif`

## Build from Source

To build the AppImage locally:

```bash
git clone https://github.com/RetakJunior/RL-Studio.git
cd RL-Studio
./packaging/build-appimage.sh
```

The output binary will be created in `dist/RLStudio-x86_64.AppImage`.

## License

GPL-3.0-or-later. See upstream Krita & KDE licenses for component details.
