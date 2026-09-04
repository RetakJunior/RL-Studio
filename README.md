<div align="center">

# 🎨 RL Studio

**Professional Digital Painting & Concept Art Studio for Linux**

[![PyPI version](https://img.shields.io/pypi/v/rlstudio.svg?color=blue)](https://pypi.org/project/rlstudio/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-green.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Platform: Linux](https://img.shields.io/badge/Platform-Linux-orange.svg)](https://github.com/RetakJunior/RL-Studio)
[![Release](https://img.shields.io/github/v/release/RetakJunior/RL-Studio?color=red)](https://github.com/RetakJunior/RL-Studio/releases)

<p align="center">
  <img src="logos/RL Studio.png" alt="RL Studio Splash Screen" width="680"/>
</p>

</div>

---

## Overview

**RL Studio** is an advanced desktop digital painting, concept art, and raster illustration suite for Linux. Engineered for high performance and creative flexibility, it features a modern responsive UI, multi-layer engine, hardware-accelerated canvas, customizable brushes, and native standalone portability.

### ✨ Key Features

- **Standalone Linux AppImage**: Single-file executable with zero installation required. Works on Debian, Ubuntu, Fedora, Arch, and all major Linux distributions.
- **Dedicated `.rls` Document Format**: Save and open projects directly in RL Studio's native `.rls` format.
- **Custom Branding**: Fully customized splash screen, desktop icons, dialog headers, and interface accents.
- **PyPI Integration**: Install and manage via `pip install rlstudio`.
- **Advanced Brush Engines**: Full tablet and pressure sensitivity support with sub-pixel rendering.

---

## Getting Started

### 1. Download Standalone AppImage

Get the latest prebuilt AppImage from [GitHub Releases](https://github.com/RetakJunior/RL-Studio/releases):

```bash
# Make executable
chmod +x RLStudio-x86_64.AppImage

# Launch RL Studio
./RLStudio-x86_64.AppImage
```

### 2. Python / PyPI CLI

Install the official launcher package from [PyPI](https://pypi.org/project/rlstudio/):

```bash
pip install rlstudio

# Run
rlstudio
```

---

## 📁 Native File Format (`.rls`)

RL Studio saves project files with the `.rls` extension by default:

- **Default Format**: `.rls` (RL Studio Document)
- **MIME Type**: `application/x-rlstudio`
- **Backward Compatibility**: Fully compatible with existing `.kra` projects.

---

## 🛠️ Building from Source

To build the AppImage locally from the repository:

```bash
# Clone the repository
git clone https://github.com/RetakJunior/RL-Studio.git
cd RL-Studio

# Run the packaging build script
./packaging/build-appimage.sh
```

The output AppImage will be placed in the `dist/` directory:

```
dist/RLStudio-x86_64.AppImage
```

---

## 📂 Project Structure

```text
RL-Studio/
├── logos/                  # Brand logos and high-resolution splash screens
├── packaging/
│   ├── AppRun              # AppImage runtime entrypoint & environment setup
│   ├── build-appimage.sh   # Automated AppImage build pipeline
│   ├── generate_assets.py  # Multi-resolution icon generator
│   ├── patch_binaries.py   # Binary rebranding & format patching engine
│   ├── rlstudio.desktop    # Desktop environment integration
│   └── hook/
│       └── rlstudio_hook.cpp # Pure Qt5 window title, icon, and .rls format hook
├── pypi_package/           # Official PyPI package sources (rlstudio)
├── .gitignore              # Git ignore rules
└── README.md               # Project documentation
```

---

## 📄 License

This project is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0) or later.
