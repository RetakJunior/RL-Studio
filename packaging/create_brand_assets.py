#!/usr/bin/env python3
"""
RL Studio - Brand Identity & Asset Generator (0'dan Modern Tasarım)
Generates high-resolution vector and raster assets:
1. packaging/assets/rlstudio_logo.svg (Vector logo)
2. logos/logo.png (1024x1024 RGBA app icon)
3. logos/RL Studio.png & packaging/assets/splash.png (1920x1080 modern splash screen)
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGOS_DIR = os.path.join(BASE_DIR, "logos")
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(LOGOS_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

# Brand Color Palette
C_BG_DEEP   = (22, 25, 31)       # #16191F (Slate deep)
C_BG_CARD   = (33, 38, 46)       # #21262E (Studio card)
C_BORDER    = (48, 56, 68)       # #303844
C_TEAL      = (0, 173, 181)      # #00ADB5 (Neon cyan/teal)
C_TEAL_SOFT = (118, 171, 174)    # #76ABAE (Soft teal)
C_ORANGE    = (255, 87, 34)      # #FF5722 (Vibrant studio orange)
C_WHITE     = (245, 247, 250)    # #F5F7FA (Crisp white)
C_MUTED     = (140, 150, 165)    # #8C96A5 (Muted label)

def generate_svg_logo():
    """Generate high-precision scalable SVG logo."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2A303C"/>
      <stop offset="100%" stop-color="#181B22"/>
    </linearGradient>
    <linearGradient id="orangeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FF7043"/>
      <stop offset="100%" stop-color="#FF5722"/>
    </linearGradient>
    <linearGradient id="tealGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#00ADB5"/>
      <stop offset="100%" stop-color="#76ABAE"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="12" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>

  <!-- Background Squircle -->
  <rect x="24" y="24" width="464" height="464" rx="104" fill="url(#cardGrad)" stroke="#384252" stroke-width="6"/>
  <rect x="36" y="36" width="440" height="440" rx="92" fill="none" stroke="url(#tealGrad)" stroke-width="3" opacity="0.6"/>

  <!-- Creative Palette Arc -->
  <path d="M 120 370 A 180 180 0 0 1 392 370" fill="none" stroke="url(#tealGrad)" stroke-width="12" stroke-linecap="round" opacity="0.3"/>

  <!-- Letter R: Modern Studio Geometry -->
  <!-- Vertical Bar -->
  <rect x="130" y="140" width="56" height="232" rx="20" fill="#F5F7FA"/>
  <!-- Top Loop -->
  <path d="M 170 140 H 270 C 320 140 350 170 350 215 C 350 260 320 290 270 290 H 170 Z" fill="#F5F7FA"/>
  <path d="M 186 186 H 264 C 286 186 304 198 304 215 C 304 232 286 244 264 244 H 186 Z" fill="#1C2028"/>
  <!-- Dynamic Orange Leg -->
  <path d="M 240 275 L 340 372 C 348 380 360 380 368 372 L 382 358 C 390 350 390 338 382 330 L 290 245 Z" fill="url(#orangeGrad)"/>

  <!-- Stylus Dot Accent -->
  <circle cx="360" cy="155" r="32" fill="url(#orangeGrad)" filter="url(#glow)"/>
  <circle cx="360" cy="155" r="14" fill="#FFFFFF"/>

  <!-- Bottom Studio Underline -->
  <rect x="130" y="395" width="252" height="12" rx="6" fill="url(#tealGrad)"/>
</svg>
"""
    svg_path = os.path.join(ASSETS_DIR, "rlstudio_logo.svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated Vector SVG Logo: {svg_path}")

def generate_icon():
    """Generate 1024x1024 raster icon (logos/logo.png)."""
    size = 1024
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    margin = 48
    radius = 210

    # Base card
    draw.rounded_rectangle([margin, margin, size - margin, size - margin],
                           radius=radius, fill=C_BG_CARD)
    # Outer accent ring
    draw.rounded_rectangle([margin, margin, size - margin, size - margin],
                           radius=radius, outline=(56, 66, 82), width=8)
    draw.rounded_rectangle([margin + 12, margin + 12, size - margin - 12, size - margin - 12],
                           radius=radius - 12, outline=C_TEAL_SOFT, width=4)

    # Stylized R
    # Vertical Bar
    draw.rounded_rectangle([260, 280, 372, 744], radius=40, fill=C_WHITE)
    # Loop
    draw.rounded_rectangle([260, 280, 680, 580], radius=100, fill=C_WHITE)
    draw.rounded_rectangle([372, 372, 588, 488], radius=45, fill=C_BG_CARD)
    # Orange kick leg
    draw.polygon([(480, 540), (590, 540), (764, 744), (654, 744)], fill=C_ORANGE)

    # Stylus dot
    draw.ellipse([700, 270, 810, 380], fill=C_ORANGE)
    draw.ellipse([735, 305, 775, 345], fill=C_WHITE)

    # Horizontal bottom accent bar
    draw.rounded_rectangle([260, 780, 764, 808], radius=12, fill=C_TEAL)

    icon_path = os.path.join(LOGOS_DIR, "logo.png")
    img.save(icon_path, "PNG")
    print(f"Generated Master Icon: {icon_path}")
    return img

def generate_splash():
    """Generate clean, modern 1920x1080 splash banner faithful to RL Studio palette."""
    w, h = 1920, 1080
    img = Image.new("RGB", (w, h), C_BG_DEEP)
    draw = ImageDraw.Draw(img)

    # 1. Subtle Background Grid & Geometric Aesthetic
    for x in range(0, w + 120, 96):
        draw.line([(x, 0), (x, h)], fill=(28, 33, 42), width=1)
    for y in range(0, h + 120, 96):
        draw.line([(0, y), (w, y)], fill=(28, 33, 42), width=1)

    # Gentle diagonal beam lines (Creative studio ambient)
    draw.line([(0, 200), (w, 550)], fill=(0, 173, 181), width=3)
    draw.line([(0, 220), (w, 570)], fill=(0, 173, 181), width=1)

    # 2. Central Studio Hero Card (Glassmorphism look)
    card_w, card_h = 1380, 640
    cx1 = (w - card_w) // 2
    cy1 = (h - card_h) // 2
    cx2 = cx1 + card_w
    cy2 = cy1 + card_h

    # Card background & borders
    draw.rounded_rectangle([cx1, cy1, cx2, cy2], radius=36, fill=(28, 33, 42))
    draw.rounded_rectangle([cx1, cy1, cx2, cy2], radius=36, outline=(48, 58, 74), width=4)
    draw.rounded_rectangle([cx1 + 4, cy1 + 4, cx2 - 4, cy2 - 4], radius=32, outline=C_TEAL, width=2)

    # 3. Logo Emblem on Left Side of Card
    icon = generate_icon().resize((340, 340), Image.Resampling.LANCZOS)
    img.paste(icon, (cx1 + 100, cy1 + 150), icon)

    # 4. Typography (Clean, geometric shapes for razor-sharp rendering)
    # Brand Title: RL STUDIO
    tx = cx1 + 490
    ty = cy1 + 175

    # "R"
    draw.rounded_rectangle([tx, ty, tx + 30, ty + 120], radius=10, fill=C_WHITE)
    draw.rounded_rectangle([tx, ty, tx + 105, ty + 68], radius=16, fill=C_WHITE)
    draw.rounded_rectangle([tx + 30, ty + 18, tx + 75, ty + 50], radius=8, fill=(28, 33, 42))
    draw.polygon([(tx + 60, ty + 62), (tx + 95, ty + 62), (tx + 125, ty + 120), (tx + 90, ty + 120)], fill=C_ORANGE)

    # "L"
    lx = tx + 150
    draw.rounded_rectangle([lx, ty, lx + 30, ty + 120], radius=10, fill=C_WHITE)
    draw.rounded_rectangle([lx, ty + 90, lx + 90, ty + 120], radius=10, fill=C_WHITE)

    # "STUDIO" Tag
    sx = lx + 130
    draw.rounded_rectangle([sx, ty + 20, sx + 290, ty + 85], radius=14, fill=C_ORANGE)
    # Studio text block
    draw.text((sx + 24, ty + 32), "STUDIO", fill=C_WHITE, font=None)

    # Subtitle: Digital Art & Concept Suite
    draw.rounded_rectangle([tx, ty + 150, tx + 620, ty + 195], radius=10, fill=(38, 45, 58))
    draw.text((tx + 24, ty + 160), "PROFESSIONAL DIGITAL PAINTING & CONCEPT SUITE", fill=C_TEAL, font=None)

    # Version & Status Badges
    draw.rounded_rectangle([tx, ty + 225, tx + 190, ty + 265], radius=8, fill=C_TEAL)
    draw.text((tx + 18, ty + 235), "v1.1.7 LTS", fill=(18, 22, 28), font=None)

    draw.rounded_rectangle([tx + 210, ty + 225, tx + 430, ty + 265], radius=8, fill=(38, 45, 58))
    draw.text((tx + 225, ty + 235), "STANDALONE LINUX", fill=C_WHITE, font=None)

    # Bottom Progress/Loading accent bar
    bar_y = cy2 - 70
    draw.line([(cx1 + 80, bar_y), (cx2 - 80, bar_y)], fill=(45, 54, 68), width=4)
    draw.line([(cx1 + 80, bar_y), (cx1 + 420, bar_y)], fill=C_TEAL, width=4)
    draw.text((cx1 + 80, bar_y + 16), "INITIALIZING WORKSPACE & PLUGINS...", fill=C_MUTED, font=None)

    # Bottom Right Creator Note
    draw.text((cx2 - 320, bar_y + 16), "RL Studio Creative Team", fill=C_MUTED, font=None)

    # Save to both target locations
    splash_path1 = os.path.join(LOGOS_DIR, "RL Studio.png")
    img.save(splash_path1, "PNG")

    splash_path2 = os.path.join(ASSETS_DIR, "splash.png")
    img.save(splash_path2, "PNG")
    img.save(os.path.join(ASSETS_DIR, "splash_screen.png"), "PNG")
    img.save(os.path.join(ASSETS_DIR, "0.png"), "PNG")
    img.save(os.path.join(ASSETS_DIR, "hd.jpg"), "JPEG", quality=95)

    print(f"Generated High-Res Splash Banner: {splash_path1} and {splash_path2}")

if __name__ == "__main__":
    generate_svg_logo()
    generate_icon()
    generate_splash()
    print("All modern branding assets generated successfully!")
