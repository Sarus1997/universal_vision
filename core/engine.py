# core/engine.py
from ultralytics import YOLO

from config.labels import THAI_NAMES
from core.targets import resolve_targets
from rendering.visualizer import render_hud, thai_font_available


class UniversalVisionEngine:
    def __init__(self, model_name="yolov8m-seg.pt"):
        self.model = YOLO(model_name)
        self.names = self.model.names  # {id: english_name}

    # ---------- helpers ----------
    def resolve(self, query):
        return resolve_targets(query, self.names)

    def display_name(self, cls_id, lang="th"):
        en = self.names[cls_id]
        if lang == "th" and thai_font_available():
            return THAI_NAMES.get(en, en)
        return en

    def reset_tracker(self):
        """เรียกก่อนเริ่มวิดีโอใหม่ เพื่อรีเซ็ต ID ของ tracker"""
        self.model.predictor = None

    # ---------- main ----------
    def process_frame(self, frame, conf=0.35, iou=0.5, imgsz=960, target_ids=None,
                      show_masks=True, show_boxes=True, track=False, augment=False,
                      retina=True, max_det=300, lang="th", fps=None, frame_idx=None, analytics=None):
        kw = dict(conf=conf, iou=iou, imgsz=imgsz, classes=target_ids or None,
                  retina_masks=retina, max_det=max_det, verbose=False)
        if track:
            res = self.model.track(frame, persist=True, tracker="bytetrack.yaml", **kw)[0]
        else:
            res = self.model.predict(frame, augment=augment, **kw)[0]

        dets = []
        n = len(res.boxes) if res.boxes is not None else 0
        if n:
            xyxy = res.boxes.xyxy.cpu().numpy()
            confs = res.boxes.conf.cpu().numpy()
            clss = res.boxes.cls.cpu().numpy().astype(int)
            ids = (res.boxes.id.int().cpu().tolist()
                   if res.boxes.id is not None else [None] * n)
            polys = res.masks.xy if res.masks is not None else [None] * n
            for i in range(n):
                dets.append({
                    "box": xyxy[i], "conf": float(confs[i]), "cls_id": int(clss[i]),
                    "label": self.display_name(int(clss[i]), lang),
                    "en_name": self.names[int(clss[i])],
                    "track_id": ids[i], "poly": polys[i],
                })

        out = render_hud(frame, dets, show_masks=show_masks, show_boxes=show_boxes,
                         fps=fps, frame_idx=frame_idx)
        if analytics is not None:
            out = analytics.apply(out, dets, frame_idx or 0)
        stats = {}
        for d in dets:
            stats[d["label"]] = stats.get(d["label"], 0) + 1
        return out, stats, dets