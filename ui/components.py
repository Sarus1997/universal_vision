# ui/components.py
import os

import pandas as pd
import streamlit as st

from config.theme import ROOT

ACCENTS = ["#00ffff", "#00ff88", "#ff2fb9", "#ffa500", "#3d8bff", "#ffee00", "#b46bff", "#5cff5c"]



CSS_PATH = os.path.join(ROOT, "assets", "css", "style.css")


def load_custom_css():
    """โหลดสไตล์จาก assets/css/style.css"""
    try:
        with open(CSS_PATH, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"ไม่พบไฟล์สไตล์: {CSS_PATH}")


def render_hero():
    st.markdown(
        """
    <div class="hero">
      <h1>UNIVERSAL VISION HUD</h1>
      <div class="sub">ระบบตรวจจับ · แบ่งส่วน · ติดตามวัตถุ แบบเรียลไทม์ — สั่งงานด้วยภาษาไทยหรืออังกฤษ</div>
      <div class="chips">
        <span class="chip"><i></i>SYSTEM ONLINE</span>
        <span class="chip bl">YOLOv8 · SEGMENTATION</span>
        <span class="chip pk">MULTI-OBJECT TRACKING</span>
        <span class="chip">TH / EN COMMAND</span>
        <span class="chip bl">COMMAND CENTER</span>
      </div>
    </div>""",
        unsafe_allow_html=True,
    )


def banner(text):
    st.markdown(f'<div class="hud-banner">▌ {text}</div>', unsafe_allow_html=True)


def render_stats_dashboard(stats, dets=None, title="📡 DETECTED ENTITIES SUMMARY"):
    if not stats:
        st.info("💡 ไม่พบวัตถุตามเงื่อนไขที่กำหนด ลองลด Confidence หรือเปลี่ยนเป้าหมาย")
        return

    st.markdown(f"### {title}")
    total = sum(stats.values())
    items = [("TOTAL", total)] + sorted(stats.items(), key=lambda x: -x[1])
    per_row = 6
    for start in range(0, len(items), per_row):
        cols = st.columns(per_row)
        for j, (col, (name, count)) in enumerate(zip(cols, items[start:start + per_row])):
            k = start + j
            color = "#ff2fb9" if k == 0 else ACCENTS[(k - 1) % len(ACCENTS)]
            pct = 100 if k == 0 else int(100 * count / total)
            col.markdown(
                f'<div class="hud-card" style="--c:{color};animation-delay:{k * 0.07}s">'
                f'<div class="hud-val">{count}</div><div class="hud-label">{name}</div>'
                f'<div class="hud-bar"><div style="width:{pct}%"></div></div></div>',
                unsafe_allow_html=True,
            )

    c1, c2 = st.columns([1, 1])
    with c1:
        st.bar_chart(pd.DataFrame({"จำนวน": stats}), color="#00ffff")
    with c2:
        if dets:
            rows = [{
                "ID": d.get("track_id"), "วัตถุ": d["label"], "EN": d["en_name"],
                "ความมั่นใจ %": round(d["conf"] * 100, 1),
                "กว้าง": int(d["box"][2] - d["box"][0]),
                "สูง": int(d["box"][3] - d["box"][1]),
            } for d in dets]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, height=260)