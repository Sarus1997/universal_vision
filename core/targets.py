# core/targets.py
"""แปลงข้อความที่ผู้ใช้พิมพ์ (ไทย/อังกฤษ) เป็นรายการ class id ของโมเดล"""
import difflib
import re

from config.labels import ALIASES, GROUPS, THAI_NAMES

_SPLIT = re.compile(r"[,;\n/、|]+|\s+และ\s+|\s+กับ\s+|\s+and\s+", re.IGNORECASE)


def _match_token(t, name2id):
    """คืนค่า list ของชื่อ EN ที่ตรงกับ token หรือ [] ถ้าไม่พบ"""
    t = t.strip().lower()
    if not t:
        return []
    # 1) กลุ่ม
    for keys, members in GROUPS.items():
        if t in keys:
            return members
    # 2) alias
    if t in ALIASES:
        return ALIASES[t]
    # 3) ตรงเป๊ะ
    if t in name2id:
        return [t]
    th2en = {v: k for k, v in THAI_NAMES.items()}
    if t in th2en:
        return [th2en[t]]
    # 4) พหูพจน์อังกฤษ
    if t.endswith("s") and t[:-1] in name2id:
        return [t[:-1]]
    # 5) substring
    if len(t) >= 2:
        hits = [en for en, th in THAI_NAMES.items() if t in th or (len(th) >= 2 and th in t)]
        hits += [en for en in name2id if len(t) >= 3 and t in en and en not in hits]
        if hits:
            return hits
    # 6) fuzzy (พิมพ์ผิดเล็กน้อย)
    close = difflib.get_close_matches(t, list(name2id), n=1, cutoff=0.75)
    return close


def resolve_targets(query, names):
    """
    query: ข้อความจากผู้ใช้ เช่น "คน, รถ, สุนัข" / "person car dog" / "ยานพาหนะ"
    names: dict {class_id: english_name} จากโมเดล
    return: (sorted_ids, unmatched_tokens)
    """
    name2id = {v.lower(): k for k, v in names.items()}
    ids, unmatched = set(), []
    for token in _SPLIT.split(query or ""):
        token = token.strip()
        if not token:
            continue
        found = _match_token(token, name2id)
        # ถ้าทั้งวลีไม่เจอ ลองแยกตามช่องว่าง
        if not found and " " in token:
            for sub in token.split():
                sub_found = _match_token(sub, name2id)
                if sub_found:
                    found += sub_found
                else:
                    unmatched.append(sub)
        elif not found:
            unmatched.append(token)
        ids.update(name2id[n] for n in found if n in name2id)
    return sorted(ids), unmatched