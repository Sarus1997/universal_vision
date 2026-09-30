# config/theme.py — สี, ฟอนต์
import os

# โฟลเดอร์รากของโปรเจกต์ (config/ อยู่ลึกลงมาหนึ่งชั้น)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Neon palette (BGR)
NEON_PALETTE = [
    (255, 255, 0), (0, 255, 128), (255, 0, 180), (0, 165, 255),
    (255, 100, 0), (0, 255, 255), (180, 105, 255), (80, 255, 80),
    (255, 60, 255), (60, 200, 255),
]
BG_DARK = (18, 14, 10)

# ฟอนต์ที่รองรับภาษาไทย (วางไฟล์ .ttf ไว้ในโฟลเดอร์ assets/fonts/ ได้เลย เช่น Sarabun / NotoSansThai)
FONT_CANDIDATES = [
    os.path.join(ROOT, "assets", "fonts", "Sarabun-Regular.ttf"),
    os.path.join(ROOT, "assets", "fonts", "NotoSansThai-Regular.ttf"),
    os.path.join(ROOT, "assets", "fonts", "font.ttf"),
    # Windows
    "C:/Windows/Fonts/leelawui.ttf", "C:/Windows/Fonts/tahoma.ttf",
    "C:/Windows/Fonts/cordia.ttc",
    # Linux (sudo apt install fonts-thai-tlwg / fonts-noto)
    "/usr/share/fonts/truetype/tlwg/Loma.ttf",
    "/usr/share/fonts/truetype/tlwg/Garuda.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansThaiUI-Regular.ttf",
    # macOS
    "/System/Library/Fonts/Supplemental/Ayuthaya.ttf",
    "/System/Library/Fonts/Thonburi.ttc",
]