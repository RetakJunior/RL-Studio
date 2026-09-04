#!/usr/bin/env python3
"""
RL Studio - Brand Identity & Asset Generator
Generates high-resolution vector-quality assets:
1. logos/logo.png (1024x1024 RGBA app icon)
2. logos/RL Studio.png (1536x1024 RGB splash screen)
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGOS_DIR = os.path.join(BASE_DIR, "logos")
os.makedirs(LOGOS_DIR, exist_ok=True)

# Brand Palette
C_DARK = (48, 56, 65)        # #303841
C_DEEP = (34, 40, 49)        # #222831
C_LIGHT = (245, 245, 245)    # #F5F5F5
C_TEAL = (118, 171, 174)     # #76ABAE
C_ORANGE = (255, 87, 34)     # #FF5722
C_ACCENT = (255, 112, 67)    # #FF7043

# ==========================================
# 1. Generate 1024x1024 App Icon (logo.png)
# ==========================================
def generate_icon():
    size = 1024
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Smooth rounded squircle background
    margin = 48
    radius = 200
    draw.rounded_rectangle([margin, margin, size - margin, size - margin],
                           radius=radius, fill=C_DARK)

    # Subtle inner border
    draw.rounded_rectangle([margin + 4, margin + 4, size - margin - 4, size - margin - 4],
                           radius=radius - 4, outline=C_TEAL, width=8)

    # Stylized Geometric 'R' & 'L' Studio Monogram
    # Left vertical stem of R
    draw.rounded_rectangle([260, 240, 360, 780], radius=40, fill=C_LIGHT)
    
    # Upper bowl of R
    draw.rounded_rectangle([260, 240, 680, 500], radius=50, fill=C_LIGHT)
    draw.rounded_rectangle([360, 320, 580, 420], radius=25, fill=C_DARK)

    # Diagonal leg of R with vibrant creative orange accent
    draw.polygon([(460, 480), (580, 480), (740, 780), (620, 780)], fill=C_ORANGE)

    # Creative dynamic stylus swoosh / dot
    draw.ellipse([640, 220, 740, 320], fill=C_TEAL)
    draw.polygon([(690, 220), (740, 160), (790, 220)], fill=C_ORANGE)

    icon_path = os.path.join(LOGOS_DIR, "logo.png")
    img.save(icon_path, "PNG")
    print(f"Generated Icon: {icon_path}")
    return img

# ==========================================
# 2. Generate 1536x1024 Splash Screen
# ==========================================
def generate_splash():
    width, height = 1536, 1024
    img = Image.new("RGB", (width, height), C_DEEP)
    draw = ImageDraw.Draw(img)

    # Elegant subtle diagonal studio texture / grid
    for x in range(-height, width + height, 80):
        draw.line([(x, 0), (x + height, height)], fill=(40, 46, 56), width=2)

    # Central artwork frame
    frame_m = 32
    draw.rectangle([frame_m, frame_m, width - frame_m, height - frame_m], outline=(60, 70, 82), width=3)

    # Studio decorative art elements
    # Left stylized art flow
    points = []
    for step in range(120):
        t = step / 120.0
        px = 120 + 380 * math.sin(t * math.pi)
        py = 100 + t * 820
        points.append((px, py))
    draw.line(points, fill=C_TEAL, width=8)

    # Glowing geometric creative circles
    for r, col in [(240, (50, 60, 72)), (180, (60, 75, 90)), (120, C_TEAL)]:
        draw.ellipse([width - 480 - r, 300 - r, width - 480 + r, 300 + r], outline=col, width=4)
    draw.ellipse([width - 480 - 60, 300 - 60, width - 480 + 60, 300 + 60], fill=C_ORANGE)

    # Prominent RL STUDIO Brand Typography
    # Draw logo emblem
    logo_sub = generate_icon().resize((220, 220), Image.Resampling.LANCZOS)
    img.paste(logo_sub, (200, 380), logo_sub)

    # Render Bold Typography using shapes
    # Main title "RL STUDIO"
    # "R"
    rx, ry = 480, 400
    draw.rounded_rectangle([rx, ry, rx + 40, ry + 160], radius=15, fill=C_LIGHT)
    draw.rounded_rectangle([rx, ry, rx + 130, ry + 85], radius=20, fill=C_LIGHT)
    draw.rounded_rectangle([rx + 40, ry + 25, rx + 95, ry + 60], radius=8, fill=C_DEEP)
    draw.polygon([(rx + 70, ry + 80), (rx + 115, ry + 80), (rx + 150, ry + 160), (rx + 105, ry + 160)], fill=C_ORANGE)

    # "L"
    lx, ly = 660, 400
    draw.rounded_rectangle([lx, ly, lx + 40, ry + 160], radius=15, fill=C_LIGHT)
    draw.rounded_rectangle([lx, ly + 120, lx + 120, ly + 160], radius=15, fill=C_LIGHT)

    # "STUDIO" banner
    draw.rounded_rectangle([480, 585, 920, 635], radius=12, fill=C_TEAL)
    
    # Subtitle line
    draw.text((485, 595), "D I G I T A L   P A I N T I N G   S U I T E", fill=C_DEEP)
    
    # Version & System badge
    draw.rounded_rectangle([480, 660, 680, 695], radius=8, fill=C_DARK)
    draw.text((495, 668), "v1.0 LTS  |  LINUX", fill=C_LIGHT)

    # Bottom status bar
    draw.line([(200, 880), (width - 200, 880)], fill=(70, 80, 95), width=2)
    draw.text((200, 895), "INITIALIZING CREATIVE ENGINE...", fill=C_TEAL)

    splash_path = os.path.join(LOGOS_DIR, "RL Studio.png")
    img.save(splash_path, "PNG")
    print(f"Generated Splash: {splash_path}")

if __name__ == "__main__":
    generate_icon()
    generate_splash()
    print("Branding assets generated successfully.")
