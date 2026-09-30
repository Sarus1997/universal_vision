# config/labels.py — ชื่อไทย, กลุ่มคำ, คำพ้อง (แก้ที่นี่เมื่ออยากเพิ่มคำ)

# ชื่อไทยของ 80 คลาส COCO
THAI_NAMES = {
    "person": "คน", "bicycle": "จักรยาน", "car": "รถยนต์", "motorcycle": "มอเตอร์ไซค์",
    "airplane": "เครื่องบิน", "bus": "รถบัส", "train": "รถไฟ", "truck": "รถบรรทุก",
    "boat": "เรือ", "traffic light": "ไฟจราจร", "fire hydrant": "หัวดับเพลิง",
    "stop sign": "ป้ายหยุด", "parking meter": "มิเตอร์จอดรถ", "bench": "ม้านั่ง",
    "bird": "นก", "cat": "แมว", "dog": "สุนัข", "horse": "ม้า", "sheep": "แกะ",
    "cow": "วัว", "elephant": "ช้าง", "bear": "หมี", "zebra": "ม้าลาย", "giraffe": "ยีราฟ",
    "backpack": "เป้สะพายหลัง", "umbrella": "ร่ม", "handbag": "กระเป๋าถือ", "tie": "เนคไท",
    "suitcase": "กระเป๋าเดินทาง", "frisbee": "จานร่อน", "skis": "สกี",
    "snowboard": "สโนว์บอร์ด", "sports ball": "ลูกบอล", "kite": "ว่าว",
    "baseball bat": "ไม้เบสบอล", "baseball glove": "ถุงมือเบสบอล",
    "skateboard": "สเก็ตบอร์ด", "surfboard": "กระดานโต้คลื่น", "tennis racket": "ไม้เทนนิส",
    "bottle": "ขวด", "wine glass": "แก้วไวน์", "cup": "แก้วน้ำ", "fork": "ส้อม",
    "knife": "มีด", "spoon": "ช้อน", "bowl": "ชาม", "banana": "กล้วย", "apple": "แอปเปิล",
    "sandwich": "แซนด์วิช", "orange": "ส้ม", "broccoli": "บรอกโคลี", "carrot": "แครอท",
    "hot dog": "ฮอตดอก", "pizza": "พิซซ่า", "donut": "โดนัท", "cake": "เค้ก",
    "chair": "เก้าอี้", "couch": "โซฟา", "potted plant": "ต้นไม้กระถาง", "bed": "เตียง",
    "dining table": "โต๊ะอาหาร", "toilet": "โถส้วม", "tv": "โทรทัศน์", "laptop": "แล็ปท็อป",
    "mouse": "เมาส์", "remote": "รีโมท", "keyboard": "คีย์บอร์ด", "cell phone": "โทรศัพท์มือถือ",
    "microwave": "ไมโครเวฟ", "oven": "เตาอบ", "toaster": "เครื่องปิ้งขนมปัง",
    "sink": "อ่างล้างจาน", "refrigerator": "ตู้เย็น", "book": "หนังสือ", "clock": "นาฬิกา",
    "vase": "แจกัน", "scissors": "กรรไกร", "teddy bear": "ตุ๊กตาหมี",
    "hair drier": "ไดร์เป่าผม", "toothbrush": "แปรงสีฟัน",
}

# กลุ่มคำ (พิมพ์ชื่อกลุ่มเพื่อเลือกหลายคลาสพร้อมกัน)
GROUPS = {
    ("ยานพาหนะ", "พาหนะ", "vehicle", "vehicles", "transport"): [
        "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat"],
    ("สัตว์", "animal", "animals"): [
        "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe"],
    ("อาหาร", "food"): [
        "banana", "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake"],
    ("อิเล็กทรอนิกส์", "อุปกรณ์อิเล็กทรอนิกส์", "electronics", "gadget", "gadgets"): [
        "tv", "laptop", "mouse", "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "refrigerator"],
    ("เฟอร์นิเจอร์", "furniture"): ["chair", "couch", "potted plant", "bed", "dining table", "toilet"],
    ("เครื่องครัว", "kitchen", "tableware"): ["bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl"],
    ("กีฬา", "sport", "sports"): [
        "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
        "baseball glove", "skateboard", "surfboard", "tennis racket"],
    ("กระเป๋า", "bag", "bags"): ["backpack", "handbag", "suitcase"],
}

# คำเรียกอื่น / ภาษาพูด
ALIASES = {
    "รถ": ["car", "bus", "truck", "motorcycle"], "คน": ["person"], "ผู้คน": ["person"],
    "ผู้ชาย": ["person"], "ผู้หญิง": ["person"], "เด็ก": ["person"], "people": ["person"],
    "man": ["person"], "woman": ["person"], "human": ["person"],
    "มอไซค์": ["motorcycle"], "มอเตอร์ไซด์": ["motorcycle"], "จักรยานยนต์": ["motorcycle"],
    "bike": ["bicycle", "motorcycle"], "มือถือ": ["cell phone"], "โทรศัพท์": ["cell phone"],
    "phone": ["cell phone"], "smartphone": ["cell phone"], "หมา": ["dog"], "น้องหมา": ["dog"],
    "น้องแมว": ["cat"], "ทีวี": ["tv"], "television": ["tv"], "คอม": ["laptop"],
    "คอมพิวเตอร์": ["laptop"], "notebook": ["laptop"], "โน้ตบุ๊ก": ["laptop"],
    "ต้นไม้": ["potted plant"], "plant": ["potted plant"], "table": ["dining table"],
    "โต๊ะ": ["dining table"], "sofa": ["couch"], "ตู้เย็น": ["refrigerator"], "fridge": ["refrigerator"],
    "ลูกบอล": ["sports ball"], "ball": ["sports ball"], "football": ["sports ball"], "ฟุตบอล": ["sports ball"],
    "ไฟแดง": ["traffic light"], "ร่ม": ["umbrella"], "รถเมล์": ["bus"], "เครื่องบิน": ["airplane"],
    "plane": ["airplane"], "glass": ["wine glass", "cup"], "แก้ว": ["wine glass", "cup"],
    "กระเป๋า": ["backpack", "handbag", "suitcase"], "bag": ["backpack", "handbag", "suitcase"],
}