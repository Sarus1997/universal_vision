# app.py
import os
import tempfile
import time

import cv2
import numpy as np
import streamlit as st
from PIL import Image, ImageOps

from core.engine import UniversalVisionEngine
from core.analytics import SceneAnalytics
from config.labels import THAI_NAMES
from ui.components import banner, load_custom_css, render_hero, render_stats_dashboard
from rendering.visualizer import thai_font_available

st.set_page_config(page_title="Universal Vision HUD", page_icon="👁️", layout="wide")
load_custom_css()


@st.cache_resource
def get_engine(model_name):
    return UniversalVisionEngine(model_name)


render_hero()

# ======================= SIDEBAR =======================
with st.sidebar:
    st.header("🎛️ CONTROLS")

    st.subheader("🧠 โมเดล")
    model_name = st.selectbox(
        "ขนาดโมเดล (ใหญ่ = แม่นขึ้น แต่ช้าลง)",
        ["yolov8n-seg.pt", "yolov8s-seg.pt", "yolov8m-seg.pt", "yolov8l-seg.pt", "yolov8x-seg.pt"],
        index=2,
    )
    engine = get_engine(model_name)

    st.subheader("🎯 เลือกสิ่งที่ต้องการตรวจ")
    query = st.text_input(
        "พิมพ์ชื่อวัตถุ (ไทย / English)",
        placeholder="เช่น: คน, รถ, สุนัข  หรือ  person, car, dog  หรือ  ยานพาหนะ",
        help="คั่นด้วย , หรือเว้นวรรค ได้ | รองรับกลุ่มคำ เช่น ยานพาหนะ สัตว์ อาหาร อิเล็กทรอนิกส์ เฟอร์นิเจอร์",
    )
    all_ids = sorted(engine.names)
    use_thai_labels = thai_font_available()
    fmt = (lambda i: f"{THAI_NAMES.get(engine.names[i], engine.names[i])}  ({engine.names[i]})")
    picked = st.multiselect("หรือเลือกจากรายการ", all_ids, format_func=fmt)

    typed_ids, unmatched = engine.resolve(query) if query.strip() else ([], [])
    target_ids = sorted(set(typed_ids) | set(picked))
    if unmatched:
        st.warning("ไม่รู้จักคำว่า: " + ", ".join(unmatched))
    if target_ids:
        st.success("กำลังค้นหา: " + ", ".join(fmt(i).split("  (")[0] for i in target_ids))
    else:
        st.info("ไม่ได้เลือก = ตรวจทุกวัตถุ (80 ชนิด)")

    st.subheader("🔬 ความละเอียดการตรวจจับ")
    conf_thresh = st.slider("Confidence", 0.05, 1.0, 0.30, step=0.05)
    iou_thresh = st.slider("IoU (ลดกรอบซ้อน)", 0.1, 0.9, 0.5, step=0.05)
    imgsz = st.select_slider("Image Size (สูง = จับของเล็กได้ดีขึ้น)", [640, 960, 1280, 1600], value=960)
    augment = st.checkbox("TTA (แม่นขึ้น ช้าลง — เฉพาะรูปภาพ)", value=False)
    retina = st.checkbox("Hi-res Masks (ขอบ mask ละเอียด)", value=True)
    max_det = st.number_input("จำนวนวัตถุสูงสุด", 10, 1000, 300, step=10)

    st.subheader("🎨 การแสดงผล")
    show_masks = st.checkbox("Segmentation Masks + Glow", value=True)
    show_boxes = st.checkbox("กรอบ HUD + เป้าเล็ง", value=True)
    lang = "th" if st.radio("ภาษาป้ายชื่อ", ["ไทย", "English"], horizontal=True) == "ไทย" else "en"
    if lang == "th" and not use_thai_labels:
        st.error("ไม่พบฟอนต์ไทยในเครื่อง → ป้ายบนภาพจะเป็น English\n\nวางไฟล์ Sarabun-Regular.ttf ไว้ในโฟลเดอร์ assets/fonts/")

with st.sidebar:
    st.subheader("🛰️ COMMAND CENTER (วิดีโอ + Tracking)")
    ana_trails = st.checkbox("เส้นทางเคลื่อนที่ (Trails)", value=True)
    ana_heat = st.checkbox("Heatmap ความหนาแน่น", value=False)
    ana_line = st.checkbox("เส้นนับผ่าน IN / OUT", value=False)
    line_y = st.slider("ตำแหน่งเส้น (% จากบน)", 10, 90, 50) / 100
    ana_zone = st.checkbox("โซนหวงห้าม + แจ้งเตือนบุกรุก", value=False)
    zx = st.slider("โซน แนวนอน (%)", 0, 100, (55, 95))
    zy = st.slider("โซน แนวตั้ง (%)", 0, 100, (50, 95))

common = dict(conf=conf_thresh, iou=iou_thresh, imgsz=imgsz, target_ids=target_ids,
              show_masks=show_masks, show_boxes=show_boxes, retina=retina,
              max_det=int(max_det), lang=lang)

tab_img, tab_vid = st.tabs(["📸 ตรวจสอบรูปภาพ", "🎥 ตรวจสอบวิดีโอ"])

# ======================= TAB 1: IMAGE =======================
with tab_img:
    banner("IMAGE SCAN MODE — อัปโหลดรูปเพื่อสแกนวัตถุ")
    img_file = st.file_uploader("อัปโหลดรูปภาพ", type=["jpg", "png", "jpeg", "webp", "bmp"])
    if img_file:
        pil_img = ImageOps.exif_transpose(Image.open(img_file)).convert("RGB")
        bgr_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        col1, col2 = st.columns(2)
        with col1:
            st.image(pil_img, caption="RAW INPUT", use_container_width=True)
        with col2:
            with st.spinner("AI กำลังสแกน..."):
                t0 = time.time()
                out_bgr, stats, dets = engine.process_frame(bgr_img, augment=augment, **common)
                dt = time.time() - t0
            out_rgb = cv2.cvtColor(out_bgr, cv2.COLOR_BGR2RGB)
            st.image(out_rgb, caption=f"HUD OUTPUT  ({dt:.2f}s)", use_container_width=True)

        render_stats_dashboard(stats, dets)

        ok, buf = cv2.imencode(".png", out_bgr)
        if ok:
            st.download_button("⬇️ ดาวน์โหลดภาพผลลัพธ์", buf.tobytes(), "hud_result.png", "image/png")

# ======================= TAB 2: VIDEO =======================
with tab_vid:
    banner("VIDEO TRACKING MODE — ตรวจจับ + ติดตามวัตถุพร้อมหมายเลข ID")
    vid_file = st.file_uploader("อัปโหลดวิดีโอ", type=["mp4", "avi", "mov", "mkv"])
    if vid_file:
        c1, c2, c3, c4 = st.columns(4)
        track = c1.checkbox("ติดตามวัตถุ (Tracking + ID)", value=True)
        skip = c2.number_input("ข้ามเฟรม (เร็วขึ้น)", 0, 10, 1)
        width = c3.select_slider("ความกว้างวิดีโอ", [640, 960, 1280], value=960)
        save_out = c4.checkbox("บันทึกวิดีโอผลลัพธ์", value=False)

        start = st.button("▶️ เริ่มประมวลผล")  # คลิกปุ่มนี้ซ้ำ/ปุ่มอื่น = หยุด
        frame_window = st.empty()
        prog = st.progress(0.0)
        live = st.empty()

        if start:
            suffix = os.path.splitext(vid_file.name)[1] or ".mp4"
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            tmp.write(vid_file.getvalue())
            tmp.close()

            cap = cv2.VideoCapture(tmp.name)
            total = max(1, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
            src_fps = cap.get(cv2.CAP_PROP_FPS) or 25
            engine.reset_tracker()
            ana = SceneAnalytics(
                trails=ana_trails and track, heatmap=ana_heat,
                line_y=line_y if (ana_line and track) else None,
                zone=(zx[0] / 100, zy[0] / 100, zx[1] / 100, zy[1] / 100) if ana_zone else None)

            writer, out_path = None, None
            seen, peak = {}, {}
            idx, t_last, fps = 0, time.time(), 0.0

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                idx += 1
                if skip and (idx % (skip + 1)) != 0:
                    continue

                h0, w0 = frame.shape[:2]
                frame = cv2.resize(frame, (width, int(h0 * width / w0)))
                out, stats, dets = engine.process_frame(
                    frame, track=track, fps=fps, frame_idx=idx, analytics=ana, **common)

                now = time.time()
                fps = 0.8 * fps + 0.2 * (1.0 / max(now - t_last, 1e-3)) if fps else 1.0 / max(now - t_last, 1e-3)
                t_last = now

                for d in dets:  # สถิติ: นับเฉพาะ ID ไม่ซ้ำเมื่อ tracking
                    if track and d["track_id"] is not None:
                        seen.setdefault(d["label"], set()).add(d["track_id"])
                for k, v in stats.items():
                    peak[k] = max(peak.get(k, 0), v)

                if save_out:
                    if writer is None:
                        out_path = os.path.join(tempfile.gettempdir(), "hud_output.mp4")
                        writer = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*"mp4v"),
                                                 src_fps / (skip + 1), (out.shape[1], out.shape[0]))
                    writer.write(out)

                frame_window.image(cv2.cvtColor(out, cv2.COLOR_BGR2RGB), use_container_width=True)
                prog.progress(min(idx / total, 1.0))
                live.markdown(
                    "**LIVE:** " + (" · ".join(f"{k} ×{v}" for k, v in stats.items()) or "—"))

            cap.release()
            if writer:
                writer.release()
            prog.progress(1.0)
            st.success("สิ้นสุดการวิเคราะห์วิดีโอ")

            summary = ({k: len(v) for k, v in seen.items()} if track and seen else peak)
            render_stats_dashboard(
                summary, title="📡 สรุปทั้งคลิป (นับวัตถุไม่ซ้ำ)" if track else "📡 สรุปทั้งคลิป (จำนวนสูงสุดต่อเฟรม)")
            if out_path and os.path.exists(out_path):
                with open(out_path, "rb") as f:
                    st.download_button("⬇️ ดาวน์โหลดวิดีโอผลลัพธ์", f.read(), "hud_result.mp4", "video/mp4")
            os.unlink(tmp.name)

            import pandas as pd
            rep = ana.summary()
            st.markdown("### 🛰️ COMMAND CENTER REPORT")
            if ana_line and track:
                m1, m2 = st.columns(2)
                m1.metric("เข้า (IN)", rep["in"])
                m2.metric("ออก (OUT)", rep["out"])
            if rep["timeline"]:
                import pandas as pd
                st.caption("จำนวนวัตถุตามช่วงเวลา (ต่อเฟรม)")
                st.line_chart(pd.DataFrame(rep["timeline"]))
            heat_img = ana.heat_image() if ana_heat else None
            if heat_img is not None:
                st.image(cv2.cvtColor(heat_img, cv2.COLOR_BGR2RGB),
                         caption="Heatmap ความหนาแน่นทั้งคลิป", use_container_width=True)
            if rep["events"]:
                st.dataframe(pd.DataFrame(rep["events"]), use_container_width=True, height=220)