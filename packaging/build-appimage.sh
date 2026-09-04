#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PACKAGING_DIR="${ROOT_DIR}/packaging"
APPDIR="${ROOT_DIR}/RetakAlium.AppDir"
DIST_DIR="${ROOT_DIR}/dist"

echo "========================================================"
echo "    RL Studio - Professional Linux AppImage Builder"
echo "========================================================"

# 1. Clean and prepare AppDir
rm -rf "${APPDIR}"
mkdir -p "${APPDIR}/usr/bin"
mkdir -p "${APPDIR}/usr/lib"
mkdir -p "${APPDIR}/usr/lib/x86_64-linux-gnu/kritaplugins"
mkdir -p "${APPDIR}/usr/share"
mkdir -p "${APPDIR}/usr/share/applications"
mkdir -p "${APPDIR}/usr/share/icons/hicolor"
mkdir -p "${DIST_DIR}"

# 2. Generate Brand Assets
echo "==> Generating brand assets..."
python3 "${PACKAGING_DIR}/generate_assets.py"

# 3. Compile Pure Qt5 Hook
echo "==> Compiling Qt5 Hook Library..."
mkdir -p "${PACKAGING_DIR}/hook"
g++ -shared -fPIC -std=c++17 \
    "${PACKAGING_DIR}/hook/rlstudio_hook.cpp" \
    -o "${PACKAGING_DIR}/hook/librlstudio_hook.so" \
    -I/usr/include/x86_64-linux-gnu/qt5 \
    -I/usr/include/x86_64-linux-gnu/qt5/QtCore \
    -I/usr/include/x86_64-linux-gnu/qt5/QtGui \
    -I/usr/include/x86_64-linux-gnu/qt5/QtWidgets \
    -L/usr/lib/x86_64-linux-gnu \
    -lQt5Widgets -lQt5Gui -lQt5Core -ldl
cp "${PACKAGING_DIR}/hook/librlstudio_hook.so" "${APPDIR}/usr/lib/x86_64-linux-gnu/librlstudio_hook.so"

# 4. Desktop Entry & Icons
echo "==> Installing desktop entry and icons..."
cp "${PACKAGING_DIR}/assets/rlstudio.png" "${APPDIR}/rlstudio.png"
cp "${PACKAGING_DIR}/assets/rlstudio.png" "${APPDIR}/.DirIcon"
cp "${PACKAGING_DIR}/rlstudio.desktop" "${APPDIR}/rlstudio.desktop"
cp "${PACKAGING_DIR}/rlstudio.desktop" "${APPDIR}/usr/share/applications/rlstudio.desktop"
cp "${PACKAGING_DIR}/rlstudio.desktop" "${APPDIR}/usr/share/applications/org.kde.krita.desktop"
cp "${PACKAGING_DIR}/rlstudio.desktop" "${APPDIR}/usr/share/applications/krita.desktop"

for size in 16 22 24 32 48 64 128 256 512 1024; do
    mkdir -p "${APPDIR}/usr/share/icons/hicolor/${size}x${size}/apps"
    cp "${PACKAGING_DIR}/assets/rlstudio_${size}.png" "${APPDIR}/usr/share/icons/hicolor/${size}x${size}/apps/rlstudio.png" 2>/dev/null || true
    cp "${PACKAGING_DIR}/assets/rlstudio_${size}.png" "${APPDIR}/usr/share/icons/hicolor/${size}x${size}/apps/krita.png" 2>/dev/null || true
done

# 5. Binaries
echo "==> Placing application binaries..."
if [ -f "/usr/bin/krita" ]; then
    cp /usr/bin/krita "${APPDIR}/usr/bin/rlstudio"
    ln -sf rlstudio "${APPDIR}/usr/bin/krita"
    ln -sf rlstudio "${APPDIR}/usr/bin/retakalium"
else
    echo "Error: /usr/bin/krita not found on system!" >&2
    exit 1
fi

# 6. Core Libraries and Plugins
echo "==> Bundling core libraries and plugins..."
cp -a /usr/lib/x86_64-linux-gnu/libkrita*.so* "${APPDIR}/usr/lib/x86_64-linux-gnu/" 2>/dev/null || true

if [ -d "/usr/lib/x86_64-linux-gnu/kritaplugins" ]; then
    cp -a /usr/lib/x86_64-linux-gnu/kritaplugins/* "${APPDIR}/usr/lib/x86_64-linux-gnu/kritaplugins/" 2>/dev/null || true
fi

# 7. Apply Native Rebranding Patches to libkritaui.so
echo "==> Applying native branding patches..."
TARGET_LIB="${APPDIR}/usr/lib/x86_64-linux-gnu/libkritaui.so.19.0.0"
if [ -f "${TARGET_LIB}" ]; then
    python3 "${PACKAGING_DIR}/patch_binaries.py" "${TARGET_LIB}"
else
    for candidate in "${APPDIR}/usr/lib/x86_64-linux-gnu/libkritaui"*.so*; do
        if [ ! -L "$candidate" ] && [ -f "$candidate" ]; then
            python3 "${PACKAGING_DIR}/patch_binaries.py" "$candidate"
            break
        fi
    done
fi

# 8. Shared Resources & Splash Screen
echo "==> Bundling shared data and splash screens..."
if [ -d "/usr/share/krita" ]; then
    cp -a /usr/share/krita "${APPDIR}/usr/share/"
    mkdir -p "${APPDIR}/usr/share/krita/pics"
    cp "${PACKAGING_DIR}/assets/splash.png" "${APPDIR}/usr/share/krita/pics/splash.png"
    cp "${PACKAGING_DIR}/assets/splash.png" "${APPDIR}/usr/share/krita/pics/splash_screen.png"
    cp "${PACKAGING_DIR}/assets/splash.png" "${APPDIR}/usr/share/krita/pics/0.png"
fi

if [ -d "/usr/share/color" ]; then
    cp -a /usr/share/color "${APPDIR}/usr/share/"
fi

if [ -d "/usr/share/mypaint-data" ]; then
    cp -a /usr/share/mypaint-data "${APPDIR}/usr/share/" 2>/dev/null || true
fi

# 9. Qt 5 Plugins (strictly Qt 5)
echo "==> Bundling Qt 5 plugins..."
QT5_PLUGINS="/usr/lib/x86_64-linux-gnu/qt5/plugins"
if [ -d "${QT5_PLUGINS}" ]; then
    mkdir -p "${APPDIR}/usr/plugins"
    for cat in platforms imageformats platforminputcontexts styles xcbglintegrations; do
        if [ -d "${QT5_PLUGINS}/${cat}" ]; then
            cp -a "${QT5_PLUGINS}/${cat}" "${APPDIR}/usr/plugins/" 2>/dev/null || true
        fi
    done
fi

# 10. Collect shared library dependencies
echo "==> Collecting library dependencies..."
collect_deps() {
    local binary="$1"
    if [ ! -f "$binary" ]; then return 0; fi
    ldd "$binary" 2>/dev/null | grep "=> /" | awk '{print $3}' | while read -r lib; do
        if [[ ! "$lib" =~ libc\.so && ! "$lib" =~ libpthread\.so && ! "$lib" =~ libdl\.so && ! "$lib" =~ libm\.so && ! "$lib" =~ libGL\.so && ! "$lib" =~ libdrm\.so ]]; then
            local dest="${APPDIR}/usr/lib/x86_64-linux-gnu/$(basename "$lib")"
            if [ -f "$lib" ] && [ ! -f "$dest" ]; then
                cp -L "$lib" "$dest" 2>/dev/null || true
            fi
        fi
    done
}

collect_deps "${APPDIR}/usr/bin/rlstudio"
for f in "${APPDIR}/usr/lib/x86_64-linux-gnu/libkrita"*.so*; do
    collect_deps "$f"
done
for f in "${APPDIR}/usr/plugins/platforms/"*.so; do
    collect_deps "$f"
done

# 11. Install AppRun
echo "==> Configuring AppRun..."
cp "${PACKAGING_DIR}/AppRun" "${APPDIR}/AppRun"
chmod +x "${APPDIR}/AppRun"
chmod +x "${APPDIR}/usr/bin/"* 2>/dev/null || true

# 12. Package AppImage
OUTPUT_IMAGE="${DIST_DIR}/RLStudio-x86_64.AppImage"
echo "==> Packaging executable AppImage..."
rm -f "${OUTPUT_IMAGE}"

ARCH=x86_64 appimagetool --no-appstream "${APPDIR}" "${OUTPUT_IMAGE}"
chmod +x "${OUTPUT_IMAGE}"

ln -sf "RLStudio-x86_64.AppImage" "${DIST_DIR}/RetakAlium-x86_64.AppImage"

echo "========================================================"
echo " [SUCCESS] RL Studio AppImage successfully built!"
echo " Location: ${OUTPUT_IMAGE}"
echo " Size: $(du -h "${OUTPUT_IMAGE}" | cut -f1)"
echo "========================================================"
