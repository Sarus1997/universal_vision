# core/analytics.py
"""Command Center: เส้นทางเคลื่อนที่, Heatmap, เส้นนับผ่าน In/Out, โซนหวงห้ามพร้อมแจ้งเตือน, Event log"""
import time
from collections import defaultdict, deque

import cv2
import numpy as np

from rendering.visualizer import draw_texts, get_color_by_id


class SceneAnalytics:
    def __init__(self, trails=True, heatmap=False, line_y=None, zone=None, trail_len=40):
        self.trails, self.heat_on, self.line_y, self.zone = trails, heatmap, line_y, zone
        self.tr = defaultdict(lambda: deque(maxlen=trail_len))
        self.heat = None
        self.side = {}
        self.inside = set()
        self.n_in = self.n_out = 0
        self.events, self.timeline = [], []
        self.last = None

    def _log(self, msg):
        self.events.append({"เวลา": time.strftime("%H:%M:%S"), "เหตุการณ์": msg})
        self.events = self.events[-200:]

    def _heat_overlay(self, img):
        b = cv2.GaussianBlur(self.heat, (0, 0), max(15, img.shape[1] // 40))
        n = b / (b.max() + 1e-6)
        col = cv2.applyColorMap((n * 255).astype(np.uint8), cv2.COLORMAP_JET)
        a = (n[..., None] * 0.65).astype(np.float32)
        return (img * (1 - a) + col * a).astype(np.uint8)

    def apply(self, out, dets, frame_idx=0):
        h, w = out.shape[:2]
        base = max(12, int(min(h, w) / 45))
        texts = []
        if self.heat is None:
            self.heat = np.zeros((h, w), np.float32)

        centers = []
        for d in dets:
            x1, y1, x2, y2 = d["box"]
            centers.append((int((x1 + x2) / 2), int((y1 + y2) / 2), d))
            if self.heat_on:
                self.heat[min(h - 1, int(y2)), min(w - 1, int((x1 + x2) / 2))] += 1.0
        if self.heat_on:
            out = self._heat_overlay(out)

        # ---- Trails ----
        if self.trails:
            for cx, cy, d in centers:
                if d.get("track_id") is None:
                    continue
                self.tr[d["track_id"]].append((cx, cy))
                pts = list(self.tr[d["track_id"]])
                c = get_color_by_id(d["cls_id"])
                for i in range(1, len(pts)):
                    cv2.line(out, pts[i - 1], pts[i], c, max(1, int(4 * i / len(pts))), cv2.LINE_AA)

        # ---- Counting line ----
        if self.line_y is not None:
            ly = int(self.line_y * h)
            for x in range(0, w, 24):
                cv2.line(out, (x, ly), (x + 12, ly), (255, 0, 200), 2, cv2.LINE_AA)
            for cx, cy, d in centers:
                tid = d.get("track_id")
                if tid is None:
                    continue
                s = cy > ly
                if tid in self.side and self.side[tid] != s:
                    if s:
                        self.n_in += 1
                    else:
                        self.n_out += 1
                    self._log(f"{d['label']} #{tid} ข้ามเส้น ({'IN' if s else 'OUT'})")
                self.side[tid] = s
            texts.append((f"IN {self.n_in}   OUT {self.n_out}", 12, ly + 6, (255, 0, 200), base))

        # ---- Restricted zone ----
        alert = False
        if self.zone:
            zx1, zy1, zx2, zy2 = int(self.zone[0] * w), int(self.zone[1] * h), int(self.zone[2] * w), int(self.zone[3] * h)
            now_in = {d.get("track_id", id(d)) for cx, cy, d in centers if zx1 <= cx <= zx2 and zy1 <= cy <= zy2}
            alert = bool(now_in)
            for cx, cy, d in centers:
                key = d.get("track_id", id(d))
                if key in now_in and key not in self.inside:
                    self._log(f"⚠ {d['label']} บุกรุกโซนหวงห้าม")
            self.inside = now_in
            ov = out.copy()
            cv2.rectangle(ov, (zx1, zy1), (zx2, zy2), (0, 0, 255) if alert else (0, 180, 255), -1)
            out = cv2.addWeighted(ov, 0.18 if not alert else 0.32, out, 0.82 if not alert else 0.68, 0)
            cv2.rectangle(out, (zx1, zy1), (zx2, zy2), (0, 0, 255) if alert else (0, 180, 255), 2, cv2.LINE_AA)
            texts.append(("RESTRICTED ZONE", zx1 + 6, zy1 + 4, (0, 200, 255), base))
            if alert and (frame_idx // 6) % 2 == 0:  # กะพริบ
                cv2.rectangle(out, (0, 0), (w - 1, h - 1), (0, 0, 255), max(6, w // 100))
                texts.append(("!! INTRUSION DETECTED !!", w // 2 - base * 9, h - base * 3, (60, 60, 255), int(base * 1.4)))

        self.timeline.append({"objects": len(dets), "in_zone": len(self.inside)})
        self.last = out
        return draw_texts(out, texts)

    def heat_image(self):
        if self.heat is None or self.last is None or not self.heat.any():
            return None
        return self._heat_overlay(self.last)

    def summary(self):
        return {"in": self.n_in, "out": self.n_out, "events": self.events, "timeline": self.timeline}