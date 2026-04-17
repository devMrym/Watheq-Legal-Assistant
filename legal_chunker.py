#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚖️ Watheq Chunker V13 - Dual Number Support (Text & Digits)
Handles "المادة الخامسة" and "المادة (5)" or "المادة 5".
Added: Auto-removal of "تعديلات المادة".
"""

import re
import json
import sys
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, List

# ══════════════════════════════════════════════════════════════════════════════
# Advanced Arabic Number Parser
# ══════════════════════════════════════════════════════════════════════════════

ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

UNITS = {
    "الحادية": 1, "الحادي": 1, "الأولى": 1, "الأول": 1,
    "الثانية": 2, "الثاني": 2, "الثالثة": 3, "الثالث": 3,
    "الرابعة": 4, "الرابع": 4, "الخامسة": 5, "الخامس": 5,
    "السادسة": 6, "السادس": 6, "السابعة": 7, "السابع": 7,
    "الثامنة": 8, "الثامن": 8, "التاسعة": 9, "التاسع": 9,
    "العاشرة": 10, "العاشر": 10
}

TEENS = {
    "الحادية عشر": 11, "الثانية عشر": 12, "الثالثة عشر": 13,
    "الرابعة عشر": 14, "الخامسة عشر": 15, "السادسة عشر": 16,
    "السابعة عشر": 17, "الثامنة عشر": 18, "التاسعة عشر": 19
}

TENS = {
    "العشرون": 20, "العشرين": 20, "الثلاثون": 30, "الثلاثين": 30,
    "الأربعون": 40, "الأربعين": 40, "الخمسون": 50, "الخمسين": 50,
    "الستون": 60, "الستين": 60, "السبعون": 70, "السبعين": 70,
    "الثمانون": 80, "الثمانين": 80, "التسعون": 90, "التسعين": 90
}

def arabic_ordinal_to_int(text: str) -> int:
    """Additive parser for compound Arabic ordinals and plain digits."""
    # تنظيف النص من الأقواس إذا وجدت مثل (5)
    text = text.replace("(", "").replace(")", "").strip()
    text = text.translate(ARABIC_DIGITS)
    
    # 1. التحقق إذا كان الرقم مكتوباً بشكل مباشر (أرقام)
    num_match = re.search(r'\d+', text)
    if num_match: return int(num_match.group())

    total = 0
    # 2. المئات
    if "المائتين" in text: total += 200
    elif "المائة" in text or "المئة" in text: total += 100
    
    # 3. العشرات المركبة (11-19)
    for word, val in TEENS.items():
        if word in text:
            total += val
            return total
            
    # 4. العقود (20-90)
    for word, val in TENS.items():
        if word in text:
            total += val
            break
            
    # 5. الآحاد
    for word, val in UNITS.items():
        if word in text:
            total += val
            break
            
    return total

# ══════════════════════════════════════════════════════════════════════════════
# Metadata & Extraction Logic
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class SystemMetadata:
    system_name: str = "غير محدد"
    issue_date: str = "غير محدد"
    publish_date: str = "غير محدد"
    issuing_decree: str = "غير محدد"
    last_update_decree: str = "غير محدد"
    related_regulations: List[str] = field(default_factory=list)

def clean_meta_value(val: str) -> str:
    stop_words = ["التصنيف", "نوع التشريع", "تاريخ النشر", "أداة", "وثيقة", "اخفاء"]
    for word in stop_words:
        if word in val: val = val.split(word)[0]
    return val.strip().split('\n')[0].strip()

def extract_metadata(text: str) -> SystemMetadata:
    meta = SystemMetadata()
    name_match = re.search(r"اخفاء جدول المحتوى\s*\n([^\n]+)", text)
    if not name_match:
        name_match = re.search(r"^([^\n]{5,100})\n", text)
    if name_match: meta.system_name = name_match.group(1).strip()
    
    issue = re.search(r"تاريخ الاصدار\s*([\u0600-\u06FF\d\s/]+)", text)
    if issue: meta.issue_date = clean_meta_value(issue.group(1))
    
    reg_sec = re.search(r"التشريعات المرتبطة(.*?)(?:المادة|القاعدة) (?:الأولى|1)", text, re.S)
    if reg_sec:
        content = reg_sec.group(1)
        exclude = {"التشريعات المرتبطة", meta.system_name}
        found = [l.strip().split("اخفاء")[0].strip() for l in content.splitlines() 
                 if len(l.strip()) > 5 and any(k in l for k in ["لائحة", "نظام", "قواعد"])]
        meta.related_regulations = list(dict.fromkeys([f for f in found if f not in exclude]))
    return meta

def parse_articles(text: str, meta: SystemMetadata) -> List[dict]:
    articles = []
    
    # حذف الجمل التكرارية
    text = re.sub(r'تعديلات المادة', '', text)
    
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    cur_hierarchy = {"part": None, "chapter": None}
    cur_art_ordinal = None
    cur_keyword = "المادة"
    buf = []

    def flush():
        nonlocal buf, cur_art_ordinal, cur_keyword
        if cur_art_ordinal and buf:
            idx = arabic_ordinal_to_int(cur_art_ordinal)
            safe_name = meta.system_name.replace(" ", "_")
            articles.append({
                "chunk_id": f"{safe_name}_{cur_keyword}_{idx}",
                "hierarchy": {
                    **cur_hierarchy, 
                    "label": cur_keyword,
                    "number_text": f"{cur_keyword} {cur_art_ordinal}", 
                    "index": idx
                },
                "content": {"text": "\n".join(buf).strip()}
            })
        buf = []

    for line in lines:
        if line.startswith("الباب"): flush(); cur_hierarchy["part"] = line; cur_hierarchy["chapter"] = None; continue
        if line.startswith("الفصل"): flush(); cur_hierarchy["chapter"] = line; continue
        
        # Regex مطور: يقبل "المادة الخامسة" أو "المادة (5)" أو "المادة 5"
        art_match = re.match(r'^(المادة|القاعدة)\s+([(\d)\u0600-\u06FF\s]+)', line)
        if art_match:
            flush()
            cur_keyword = art_match.group(1)
            # استخراج الرقم أو النص الترتيبي
            cur_art_ordinal = art_match.group(2).split(':')[0].strip()
            
            # إذا كان السطر يحتوي على محتوى بعد الرقم (مثل المادة 5: نص المادة)
            parts = line.split(":", 1)
            if len(parts) > 1 and parts[1].strip(): 
                buf.append(parts[1].strip())
            elif len(line.split(cur_art_ordinal)) > 1:
                # لحالات مثل "المادة 5 تخضع السجون..." بدون نقطتين رئيستين
                remaining = line.replace(f"{cur_keyword} {cur_art_ordinal}", "").strip()
                if remaining: buf.append(remaining)
            continue

        if cur_art_ordinal and not any(x in line for x in ["تاريخ النشر", "أداة إصدار", "اخفاء جدول", "التصنيف"]):
            if line != meta.system_name: buf.append(line)

    flush()
    return articles

def main():
    print("⚖️ Watheq Chunker V13 (Dual Num + Clean) - Type 'done':")
    input_text = ""
    while True:
        line = sys.stdin.readline()
        if not line or line.strip().lower() in ['done', 'تم']: break
        input_text += line
    
    meta = extract_metadata(input_text)
    articles = parse_articles(input_text, meta)
    
    safe_fn = re.sub(r'[^\w]', '_', meta.system_name) + ".json"
    with open(safe_fn, "w", encoding="utf-8") as f:
        json.dump({"system_info": asdict(meta), "articles": articles}, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Success! Extracted {len(articles)} chunks.")
    print(f"📂 Saved to: {safe_fn}")

if __name__ == "__main__":
    main()