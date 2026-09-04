#!/usr/bin/env python3
"""
RL Studio - Binary Patching Engine
1. libkritaui.so:
   - Redirects splash image to /tmp/s0.png
   - Redirects banner to /tmp/s1.svg and branding SVG to /tmp/s2.svg (RL Studio vector logo)
   - Updates artist credit to 'RL Studio'
   - Rebrands Welcome Page links ('Support RLSt', 'RLStudio Web')
   - Rebrands footer and news text to RL Studio
2. kritakraexport.so:
   - Changes default native export extension from 'kra' to 'rls'
3. kritakraimport.so:
   - Adds 'rls' to native import extensions ('rls, kra')
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
        size_offset = idx_splash - 20
        struct.pack_into("<i", data, size_offset, 11)
        new_splash = "/tmp/s0.png\x00\x00\x00".encode("utf-16le")
        data[idx_splash:idx_splash+len(old_splash)] = new_splash
        print(f"  ✓ Patched Splash Image Path at {hex(idx_splash)}")

    # 2. Patch Banner SVG (:/splash/banner.svg -> /tmp/s1.svg)
    old_banner = ":/splash/banner.svg".encode("utf-16le")
    idx_banner = data.find(old_banner)
    if idx_banner != -1:
        size_offset = idx_banner - 20
        struct.pack_into("<i", data, size_offset, 11)
        new_banner = ("/tmp/s1.svg" + "\x00" * (len(":/splash/banner.svg") - len("/tmp/s1.svg"))).encode("utf-16le")
        data[idx_banner:idx_banner+len(old_banner)] = new_banner
        print(f"  ✓ Patched Banner SVG Path at {hex(idx_banner)}")

    # 3. Patch Branding SVG (:/krita-branding.svgz -> /tmp/s2.svg)
    old_brand = ":/krita-branding.svgz".encode("utf-16le")
    idx_brand = data.find(old_brand)
    if idx_brand != -1:
        size_offset = idx_brand - 20
        struct.pack_into("<i", data, size_offset, 11)
        new_brand = ("/tmp/s2.svg" + "\x00" * (len(":/krita-branding.svgz") - len("/tmp/s2.svg"))).encode("utf-16le")
        data[idx_brand:idx_brand+len(old_brand)] = new_brand
        print(f"  ✓ Patched Branding SVG Path at {hex(idx_brand)}")

    # 4. Patch Artist Credit ('Tyson Tan' -> 'RL Studio')
    old_credit = "Tyson Tan".encode("utf-16le")
    idx_credit = data.find(old_credit)
    if idx_credit != -1:
        new_credit = "RL Studio".encode("utf-16le")
        data[idx_credit:idx_credit+len(old_credit)] = new_credit
        print(f"  ✓ Patched Artist Credit at {hex(idx_credit)}")

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

    with open(so_path, "wb") as f:
        f.write(data)
    print(f"[PATCH SUCCESS] {so_path} successfully modified!")
    return True

def patch_plugins(appdir):
    # 1. Patch Export extension (kra -> rls)
    exp_path = os.path.join(appdir, "usr/lib/x86_64-linux-gnu/kritaplugins/kritakraexport.so")
    if os.path.exists(exp_path):
        with open(exp_path, "rb") as f:
            d = bytearray(f.read())
        idx = d.find(b"X-KDE-Extensionsckra")
        if idx != -1:
            d[idx+len("X-KDE-Extensionsc"):idx+len("X-KDE-Extensionsc")+3] = b"rls"
            with open(exp_path, "wb") as f:
                f.write(d)
            print("  ✓ Patched kritakraexport.so default extension -> rls")

    # 2. Patch Import extensions (kra, krz -> rls, kra)
    imp_path = os.path.join(appdir, "usr/lib/x86_64-linux-gnu/kritaplugins/kritakraimport.so")
    if os.path.exists(imp_path):
        with open(imp_path, "rb") as f:
            d = bytearray(f.read())
        idx = d.find(b"X-KDE-Extensionshkra, krz")
        if idx != -1:
            d[idx+len("X-KDE-Extensionsh"):idx+len("X-KDE-Extensionsh")+8] = b"rls, kra"
            with open(imp_path, "wb") as f:
                f.write(d)
            print("  ✓ Patched kritakraimport.so import extensions -> rls, kra")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
        if target.endswith(".so") or target.endswith(".so.19") or target.endswith(".so.19.0.0"):
            patch_libkritaui(target)
        else:
            # Assume appdir path
            lib_candidate = os.path.join(target, "usr/lib/x86_64-linux-gnu/libkritaui.so.19.0.0")
            if os.path.exists(lib_candidate):
                patch_libkritaui(lib_candidate)
            patch_plugins(target)
