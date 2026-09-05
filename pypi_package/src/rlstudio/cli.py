import os
import sys
import shutil
import urllib.request

APPIMAGE_DIR = os.path.expanduser("~/.local/share/rlstudio")
LOCAL_APPIMAGE = os.path.join(APPIMAGE_DIR, "RLStudio-x86_64.AppImage")

APPIMAGE_CANDIDATES = [
    os.path.expanduser("~/Şablonlar/RetakAlium Studio/dist/RLStudio-x86_64.AppImage"),
    LOCAL_APPIMAGE,
    os.path.expanduser("~/.local/bin/RLStudio-x86_64.AppImage"),
    "/usr/local/bin/RLStudio-x86_64.AppImage",
]

RELEASE_URL = "https://github.com/RetakJunior/RL-Studio/releases/download/v1.1.5/RLStudio-x86_64.AppImage"

def download_appimage():
    """Automatically download the AppImage on first launch."""
    os.makedirs(APPIMAGE_DIR, exist_ok=True)
    temp_file = LOCAL_APPIMAGE + ".part"
    print("RL Studio AppImage not found locally.")
    print(f"Downloading from: {RELEASE_URL}")
    print("Please wait...")

    try:
        def reporthook(count, block_size, total_size):
            if total_size > 0:
                percent = int(count * block_size * 100 / total_size)
                mb_downloaded = (count * block_size) / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                sys.stdout.write(f"\rDownloading: {percent}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)")
                sys.stdout.flush()

        urllib.request.urlretrieve(RELEASE_URL, temp_file, reporthook)
        print("\nDownload complete! Setting executable permissions...")
        os.rename(temp_file, LOCAL_APPIMAGE)
        os.chmod(LOCAL_APPIMAGE, 0o755)
        return LOCAL_APPIMAGE
    except Exception as e:
        if os.path.exists(temp_file):
            os.remove(temp_file)
        print(f"\nDownload error: {e}")
        print("You can download the AppImage manually from:")
        print("  https://github.com/RetakJunior/RL-Studio/releases")
        return None

def main():
    """Launch RL Studio AppImage with auto-download and FUSE bypass."""
    # Always set extract-and-run so FUSE configuration is never required
    os.environ["APPIMAGE_EXTRACT_AND_RUN"] = "1"

    for path in APPIMAGE_CANDIDATES:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            os.execv(path, [path] + sys.argv[1:])

    # If binary exists in PATH
    bin_path = shutil.which("rlstudio")
    if bin_path and os.path.abspath(bin_path) != os.path.abspath(sys.argv[0]):
        os.execv(bin_path, [bin_path] + sys.argv[1:])

    # Auto download on first launch
    downloaded = download_appimage()
    if downloaded and os.path.isfile(downloaded) and os.access(downloaded, os.X_OK):
        os.execv(downloaded, [downloaded] + sys.argv[1:])

    sys.exit(1)

if __name__ == "__main__":
    main()
