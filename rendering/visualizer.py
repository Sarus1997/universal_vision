# rendering/visualizer.py
import os
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from config.theme import BG_DARK, FONT_CANDIDATES, NEON_PALETTE

_font_cache = {}
_vig_cache = {}


def _vignette(h, w):
    """ขอบภาพมืดแบบภาพยนตร์ (cache ตามขนาดภาพ)"""
    if (h, w) not in _vig_cache:
        y, x = np.ogrid[:h, :w]
        d = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2)
        _vig_cache[(h, w)] = np.clip(1.15 - 0.45 * d ** 2, 0.5, 1.0).astype(np.float32)[..., None]
    return _vig_cache[(h, w)]


def get_font(size):
    if size in _font_cache:
        return _font_cache[size]
    font = None
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            try:
                font = ImageFont.truetype(p, size)
                break
            except Exception:
                continue
    _font_cache[size] = font
    return font


def thai_font_available():
    return get_font(16) is not None


def get_color_by_id(cls_id):
    return NEON_PALETTE[cls_id % len(NEON_PALETTE)]


def text_size(text, size):
    font = get_font(size)
    if font:
        b = font.getbbox(text)
        return b[2] - b[0], int(size * 1.3)
    (w, _), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, size / 28, 1)
    return w, int(size * 1.3)


def draw_texts(img, items):
    """items: (text, x, y_top, color_bgr, size) — วาดข้อความทั้งหมดในครั้งเดียว (รองรับภาษาไทย)"""
    if not items:
        return img
    if get_font(16):
        pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        d = ImageDraw.Draw(pil)
        for text, x, y, col, size in items:
            d.text((x, y), text, font=get_font(size), fill=(col[2], col[1], col[0]))
        return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
    for text, x, y, col, size in items:
        t = text.encode("ascii", "ignore").decode()
        cv2.putText(img, t, (x, y + int(size * 0.95)), cv2.FONT_HERSHEY_SIMPLEX,
                    size / 28, col, 1, cv2.LINE_AA)
    return img


def _corners(img, x1, y1, x2, y2, color, th, length):
    for (px, py, dx, dy) in [(x1, y1, 1, 1), (x2, y1, -1, 1), (x1, y2, 1, -1), (x2, y2, -1, -1)]:
        cv2.line(img, (px, py), (px + dx * length, py), color, th + 1, cv2.LINE_AA)
        cv2.line(img, (px, py), (px, py + dy * length), color, th + 1, cv2.LINE_AA)


def render_hud(frame, dets, show_masks=True, show_boxes=True, fps=None,
               frame_idx=None, title="UNIVERSAL VISION HUD"):
    """
    dets: list ของ dict {box, label, conf, cls_id, track_id, poly}
    frame_idx: ถ้าไม่ใช่ None จะวาดเส้นสแกนเคลื่อนที่ (สำหรับวิดีโอ)
    """
    h, w = frame.shape[:2]
    base = max(12, int(min(h, w) / 48))
    th = max(1, int(min(h, w) / 500))
    out = (frame * _vignette(h, w)).astype(np.uint8)
    texts = []

    # ---------- 1) Mask เรืองแสง + เส้นขอบ Glow ----------
    polys = [(d, d["poly"]) for d in dets if d.get("poly") is not None and len(d["poly"]) >= 3]
    if show_masks and polys:
        overlay = out.copy()
        glow = np.zeros_like(out)
        for d, p in polys:
            pts = p.astype(np.int32).reshape(-1, 1, 2)
            c = get_color_by_id(d["cls_id"])
            cv2.fillPoly(overlay, [pts], c)
            cv2.polylines(glow, [pts], True, c, th * 3, cv2.LINE_AA)
        out = cv2.addWeighted(overlay, 0.35, out, 0.65, 0)
        glow = cv2.GaussianBlur(glow, (0, 0), max(3, th * 3))
        out = cv2.add(out, glow)
        for d, p in polys:
            pts = p.astype(np.int32).reshape(-1, 1, 2)
            cv2.polylines(out, [pts], True, get_color_by_id(d["cls_id"]), th + 1, cv2.LINE_AA)

    # ---------- 2) เส้นสแกน ----------
    if frame_idx is not None:
        y = int((frame_idx * 10) % h)
        band = out.copy()
        cv2.rectangle(band, (0, max(0, y - 14)), (w, y), (255, 255, 0), -1)
        out = cv2.addWeighted(band, 0.10, out, 0.90, 0)
        cv2.line(out, (0, y), (w, y), (255, 255, 0), 1, cv2.LINE_AA)

    # ---------- 3) กรอบ / มุม / เป้าเล็ง / ป้ายชื่อ ----------
    bar_h = int(base * 2.4)
    for d in dets:
        x1, y1, x2, y2 = map(int, d["box"])
        c = get_color_by_id(d["cls_id"])
        bw, bh = x2 - x1, y2 - y1
        if show_boxes:
            cv2.rectangle(out, (x1, y1), (x2, y2), c, 1, cv2.LINE_AA)
            _corners(out, x1, y1, x2, y2, c, th, max(8, min(int(min(bw, bh) * 0.2), 40)))

        # เป้าเล็งกลางวัตถุ
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        r = max(4, min(bw, bh) // 12)
        cv2.circle(out, (cx, cy), r, c, 1, cv2.LINE_AA)
        cv2.line(out, (cx - r * 2, cy), (cx - r, cy), c, 1, cv2.LINE_AA)
        cv2.line(out, (cx + r, cy), (cx + r * 2, cy), c, 1, cv2.LINE_AA)
        cv2.line(out, (cx, cy - r * 2), (cx, cy - r), c, 1, cv2.LINE_AA)
        cv2.line(out, (cx, cy + r), (cx, cy + r * 2), c, 1, cv2.LINE_AA)

        # วงแหวนหมุน (lock-on)
        ang = (frame_idx or 0) * 7
        rr = r * 2 + 5
        cv2.ellipse(out, (cx, cy), (rr, rr), 0, ang, ang + 70, c, th + 1, cv2.LINE_AA)
        cv2.ellipse(out, (cx, cy), (rr, rr), 0, ang + 180, ang + 250, c, th + 1, cv2.LINE_AA)

        # ป้ายชื่อ
        tid = f"#{d['track_id']} " if d.get("track_id") is not None else ""
        label = f"{tid}{d['label']} {int(d['conf'] * 100)}%"
        tw, tht = text_size(label, base)
        pw, ph = tw + 12, tht + 4
        px, py = x1, y1 - ph - 5
        if py < bar_h:
            py = y1 + 3
        px = min(px, w - pw - 1)
        plate = out.copy()
        cv2.rectangle(plate, (px, py), (px + pw, py + ph), BG_DARK, cv2.FILLED)
        out = cv2.addWeighted(plate, 0.75, out, 0.25, 0)
        cv2.rectangle(out, (px, py), (px + pw, py + ph), c, 1, cv2.LINE_AA)
        cv2.rectangle(out, (px, py + ph), (px + int(pw * d["conf"]), py + ph + 3), c, cv2.FILLED)
        cv2.line(out, (px, py), (px, py + ph), c, 4)
        texts.append((label, px + 7, py + 1, c, base))

    # ---------- 3.5) แผงสรุปมุมซ้ายล่าง ----------
    counts = {}
    for d in dets:
        counts.setdefault(d["label"], [d["cls_id"], 0])[1] += 1
    if counts:
        rows = sorted(counts.items(), key=lambda kv: -kv[1][1])[:8]
        lh = int(base * 1.5)
        pw = int(max(text_size(f"{k}  x{v[1]}", base)[0] for k, v in rows) + base * 3)
        ph = lh * len(rows) + 10
        x0, y0 = 12, h - ph - 12
        pnl = out.copy()
        cv2.rectangle(pnl, (x0, y0), (x0 + pw, y0 + ph), BG_DARK, cv2.FILLED)
        out = cv2.addWeighted(pnl, 0.7, out, 0.3, 0)
        cv2.rectangle(out, (x0, y0), (x0 + pw, y0 + ph), (255, 255, 0), 1, cv2.LINE_AA)
        cv2.rectangle(out, (x0, y0), (x0 + 4, y0 + ph), (255, 255, 0), cv2.FILLED)
        for i, (k, (cid, n)) in enumerate(rows):
            yy = y0 + 5 + i * lh
            col = get_color_by_id(cid)
            cv2.rectangle(out, (x0 + 12, yy + 5), (x0 + 12 + base // 2, yy + 5 + base // 2), col, cv2.FILLED)
            texts.append((f"{k}  x{n}", x0 + 14 + base, yy, col, base))

    # ---------- 4) แถบ HUD ด้านบน + กรอบมุมทั้งภาพ ----------
    top = out.copy()
    cv2.rectangle(top, (0, 0), (w, bar_h), BG_DARK, cv2.FILLED)
    out = cv2.addWeighted(top, 0.7, out, 0.3, 0)
    cv2.line(out, (0, bar_h), (w, bar_h), (255, 255, 0), 1, cv2.LINE_AA)
    _corners(out, 4, bar_h + 4, w - 5, h - 5, (255, 255, 0), th, int(base * 2))

    info = f"TARGETS {len(dets):02d}"
    if fps is not None:
        info += f"  |  FPS {fps:4.1f}"
    info += f"  |  {time.strftime('%H:%M:%S')}"
    iw, _ = text_size(info, base)
    texts.append((f"[ {title} ]", 10, int(base * 0.5), (255, 255, 0), base))
    texts.append((info, w - iw - 12, int(base * 0.5), (0, 255, 128), base))

    return draw_texts(out, texts)