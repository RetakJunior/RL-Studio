#!/usr/bin/env python3
"""
RL Studio - Asset Scaler and Integrator
Generates multi-resolution icons and splash assets into packaging/assets/
"""

import os
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGOS_DIR = os.path.join(BASE_DIR, "logos")
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

LOGO_SRC = os.path.join(LOGOS_DIR, "logo.png")
SPLASH_SRC = os.path.join(LOGOS_DIR, "RL Studio.png")

print(f"Loading Logo from: {LOGO_SRC}")
print(f"Loading Splash from: {SPLASH_SRC}")

logo_img = Image.open(LOGO_SRC).convert("RGBA")
icon_512 = logo_img.resize((512, 512), Image.Resampling.LANCZOS)
icon_512.save(os.path.join(ASSETS_DIR, "rlstudio.png"))
icon_512.save(os.path.join(ASSETS_DIR, "krita.png"))

for s in [16, 22, 24, 32, 48, 64, 128, 256, 512, 1024]:
    s_icon = logo_img.resize((s, s), Image.Resampling.LANCZOS)
    s_icon.save(os.path.join(ASSETS_DIR, f"rlstudio_{s}.png"))
    s_icon.save(os.path.join(ASSETS_DIR, f"krita_{s}.png"))

splash_img = Image.open(SPLASH_SRC).convert("RGB")
splash_img.save(os.path.join(ASSETS_DIR, "splash.png"), "PNG")
splash_img.save(os.path.join(ASSETS_DIR, "splash_screen.png"), "PNG")
splash_img.save(os.path.join(ASSETS_DIR, "0.png"), "PNG")
splash_img.save(os.path.join(ASSETS_DIR, "hd.jpg"), "JPEG", quality=95)

print("All assets scaled and saved in packaging/assets/")
