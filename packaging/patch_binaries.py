#!/usr/bin/env python3
"""
RL Studio - Binary Patching Engine
Safely patches string resources inside the AppDir's copy of libkritaui.so:
1. Redirects splash image to /tmp/s0.png
2. Redirects banner and branding SVG overlays to empty /tmp/s1.svg and /tmp/s2.svg
3. Updates artwork credit to 'RL Studio'
4. Rebrands Welcome Page links ('Support RLSt', 'RLStudio Web')
5. Rebrands footer text to RL Studio
"""

import os
import sys
import struct

def patch_libkritaui(so_path):
    print(f"[PATCH] Processing {so_path}...")
    if not os.path.exists(so_path):
        print(f"[ERROR] {so_path} not found!")
        return False

    with open(so_path, "rb") as f:
        data = bytearray(f.read())

    # 1. Patch Splash Screen Image (:/splash/0.png -> /tmp/s0.png)
    old_splash = ":/splash/0.png".encode("utf-16le")
    idx_splash = data.find(old_splash)
    if idx_splash != -1:
        # Update QStringData size (offset is 20 bytes before string data)
        size_offset = idx_splash - 20
        struct.pack_into("<i", data, size_offset, 11)  # new size: 11 chars
        new_splash = "/tmp/s0.png\x00\x00\x00".encode("utf-16le")
        data[idx_splash:idx_splash+len(old_splash)] = new_splash
        print(f"  ✓ Patched Splash Image Path at {hex(idx_splash)}")
    else:
        print("  ! Splash image path not found")

    # 2. Patch Banner SVG (:/splash/banner.svg -> /tmp/s1.svg)
    old_banner = ":/splash/banner.svg".encode("utf-16le")
    idx_banner = data.find(old_banner)
    if idx_banner != -1:
        size_offset = idx_banner - 20
        struct.pack_into("<i", data, size_offset, 11)
        new_banner = ("/tmp/s1.svg" + "\x00" * (len(":/splash/banner.svg") - len("/tmp/s1.svg"))).encode("utf-16le")
        data[idx_banner:idx_banner+len(old_banner)] = new_banner
        print(f"  ✓ Patched Banner SVG Path at {hex(idx_banner)}")
    else:
        print("  ! Banner SVG path not found")

    # 3. Patch Branding SVG (:/krita-branding.svgz -> /tmp/s2.svg)
    old_brand = ":/krita-branding.svgz".encode("utf-16le")
    idx_brand = data.find(old_brand)
    if idx_brand != -1:
        size_offset = idx_brand - 20
        struct.pack_into("<i", data, size_offset, 11)
        new_brand = ("/tmp/s2.svg" + "\x00" * (len(":/krita-branding.svgz") - len("/tmp/s2.svg"))).encode("utf-16le")
        data[idx_brand:idx_brand+len(old_brand)] = new_brand
        print(f"  ✓ Patched Branding SVG Path at {hex(idx_brand)}")
    else:
        print("  ! Branding SVG path not found")

    # 4. Patch Artist Credit ('Tyson Tan' -> 'RL Studio')
    old_credit = "Tyson Tan".encode("utf-16le")
    idx_credit = data.find(old_credit)
    if idx_credit != -1:
        new_credit = "RL Studio".encode("utf-16le")
        data[idx_credit:idx_credit+len(old_credit)] = new_credit
        print(f"  ✓ Patched Artist Credit at {hex(idx_credit)}")
    else:
        print("  ! Artist credit not found")

    # 5. Patch Welcome Screen Links (Support Krita -> Support RLSt)
    idx_supp = data.find(b"Support Krita\x00")
    if idx_supp != -1:
        data[idx_supp:idx_supp+14] = b"Support RLSt\x00\x00"
        print(f"  ✓ Patched 'Support Krita' link at {hex(idx_supp)}")

    # 6. Patch Welcome Screen Links (Krita Website -> RLStudio Web)
    idx_web = data.find(b"Krita Website\x00")
    if idx_web != -1:
        data[idx_web:idx_web+14] = b"RLStudio Web\x00\x00"
        print(f"  ✓ Patched 'Krita Website' link at {hex(idx_web)}")

    # 7. Patch Welcome Screen Footer
    old_footer_prefix = b"Krita is an open source and community-driven tool"
    idx_footer = data.find(old_footer_prefix)
    if idx_footer != -1:
        new_footer_prefix = b"RL Studio is a modern, high-performance tool     "
        data[idx_footer:idx_footer+len(old_footer_prefix)] = new_footer_prefix
        print(f"  ✓ Patched Welcome Page Footer at {hex(idx_footer)}")

    # 8. Patch News Column 'from krita.org' -> 'from RL Studio'
    old_news = b"from krita.org"
    idx_news = data.find(old_news)
    while idx_news != -1:
        data[idx_news:idx_news+len(old_news)] = b"from RL Studio"
        print(f"  ✓ Patched News text at {hex(idx_news)}")
        idx_news = data.find(old_news, idx_news + len(old_news))

    # Write patched library back
    with open(so_path, "wb") as f:
        f.write(data)
    print(f"[PATCH SUCCESS] {so_path} successfully modified!")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        patch_libkritaui(sys.argv[1])
    else:
        print("Usage: patch_binaries.py <path_to_libkritaui.so>")
