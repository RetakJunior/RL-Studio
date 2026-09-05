import os
import sys
import shutil

APPIMAGE_CANDIDATES = [
    os.path.expanduser("~/Şablonlar/RetakAlium Studio/dist/RLStudio-x86_64.AppImage"),
    os.path.expanduser("~/.local/bin/RLStudio-x86_64.AppImage"),
    "/usr/local/bin/RLStudio-x86_64.AppImage",
]

def main():
    """Launch RL Studio AppImage or report download instructions."""
    for path in APPIMAGE_CANDIDATES:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            os.execv(path, [path] + sys.argv[1:])

    bin_path = shutil.which("rlstudio")
    if bin_path and os.path.abspath(bin_path) != os.path.abspath(sys.argv[0]):
        os.execv(bin_path, [bin_path] + sys.argv[1:])

    print("RL Studio (v1.1.5)")
    print("Professional digital painting & concept art studio.")
    print("GitHub: https://github.com/RetakJunior/RL-Studio")
    print("\nDownload the latest Linux standalone AppImage from:")
    print("  https://github.com/RetakJunior/RL-Studio/releases\n")
    sys.exit(0)

if __name__ == "__main__":
    main()

