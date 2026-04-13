import re
import json
import os
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, List

# ══════════════════════════════════════════════════════════════════════════════
# محركات الضبط (الأرقام والبيانات الوصفية)
# ══════════════════════════════════════════════════════════════════════════════

def arabic_ordinal_to_int(text: str) -> int:
    # 1. Standardize digits
    text = text.strip().translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))
    
    # 2. Return literal digits if found
    num_match = re.search(r'\d+', text)
    if num_match: return int(num_match.group())
    
    # 3. Component Dictionaries
    hundreds = {
        "تسعمائة": 900, "ثمانمائة": 800, "سبعمائة": 700, "ستمائة": 600, 
        "خمسمائة": 500, "أربعمائة": 400, "ثلاثمائة": 300, "مائتين": 200, "مائة": 100
    }
    tens = {"العشرون": 20, "الثلاثون": 30, "الأربعون": 40, "الخمسون": 50, "الستون": 60, "السبعون": 70, "الثمانون": 80, "التسعون": 90}
    # Separate units from 'teens' indicator
    units = {"الأولى": 1, "الحادية": 1, "الثانية": 2, "الثالثة": 3, "الرابعة": 4, "الخامسة": 5, "السادسة": 6, "السابعة": 7, "الثامنة": 8, "التاسعة": 9}
    
    total = 0
    
    # Step A: Handle Hundreds
    for h_word, h_val in hundreds.items():
        if h_word in text:
            total += h_val
            break
            
    # Step B: Handle Teens (11-19) - Look for 'عشر' but NOT 'عشرون'
    if "عشر" in text and "عشرون" not in text:
        total += 10
        # Check units within the teen (e.g., الحادية عشرة)
        for u_word, u_val in units.items():
            if u_word in text:
                total += u_val
                return total # Exit early for teens
        # Special case for "العاشرة" (just 10)
        if total == 10 and "العاشرة" not in text:
            pass # Keep 10
        elif "العاشرة" in text and total == 0:
            return 10
            
    # Step C: Handle Tens (20-90)
    for t_word, t_val in tens.items():
        if t_word in text:
            total += t_val
            break
            
    # Step D: Handle Units (1-9) if not already handled by Teens
    for u_word, u_val in units.items():
        if u_word in text:
            total += u_val
            break
    
    # Special Case: Just "العاشرة" (10) or "المادة العاشرة"
    if total == 0 and "العاشرة" in text:
        total = 10

    return total


def clean_meta_value(val: str) -> str:
    stop_words = ["التصنيف", "نوع التشريع", "تاريخ النشر", "حالة التشريع", "أداة", "وثيقة", "مرفق", "رابط", "اخفاء"]
    for word in stop_words:
        if word in val:
            val = val.split(word)[0]
    return val.strip().split('\n')[0].strip()

# ══════════════════════════════════════════════════════════════════════════════
# محرك الاستخراج الرئيسي
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class ArticleMetadata:
    system_name: str = "غير محدد"
    issue_date: str = "غير محدد"
    publish_date: str = "غير محدد"
    issuing_decree: str = "غير محدد"
    last_update_decree: str = "غير محدد"
    last_update_date: str = ""
    related_regulations: List[str] = field(default_factory=list)

def extract_metadata_from_text(text: str) -> ArticleMetadata:
    meta = ArticleMetadata()
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    
    # تحسين استخراج اسم النظام: البحث عن السطر الذي يحتوي على "نظام ..." بالكامل
    for i, line in enumerate(lines):
        if "الباب الأول" in line and i > 0:
            meta.system_name = lines[i-1]
            break
        # إذا وجدنا كلمة نظام متبوعة بكلمات أخرى (وليس مجرد كلمة نظام وحيدة)
        if line.startswith("نظام ") and len(line) > 10 and len(line) < 100:
            meta.system_name = line
            break

    patterns = {
        "issue_date": r"تاريخ الاصدار\s*([\u0600-\u06FF\d\s/]+)",
        "publish_date": r"تاريخ النشر\s*([\u0600-\u06FF\d\s/]+)",
        "issuing_decree": r"أداة إصدار نظام.*?\n(المرسوم الملكي رقم [^\n]+|م/[^\n]+)",
        "last_update_decree": r"أداة إصدار آخر تحديث\s*([^\n]+)",
        "last_update_date": r"تاريخ أداة آخر تحديث\s*([\u0600-\u06FF\d\s/]+)"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.M | re.S)
        if match:
            raw_val = match.group(1).strip()
            setattr(meta, key, clean_meta_value(raw_val))
    
    # تصحيح إذا فشل استخراج أداة الإصدار الأساسية
    if meta.issuing_decree == "غير محدد" or "آخر تحديث" in meta.issuing_decree:
        match = re.search(r"أداة إصدار\s+(المرسوم الملكي رقم [^\n]+|م/\d+)", text)
        if match: meta.issuing_decree = match.group(1).strip()

    reg_sec = re.search(r"التشريعات المرتبطة(.*?)المادة الأولى", text, re.S)
    if reg_sec:
        content = reg_sec.group(1)
        exclude = {"التشريعات المرتبطة", "اللائحة المرتبطة بالنظام", "اللائحة التنفيذية للنظام", meta.system_name}
        found = []
        for line in content.splitlines():
            line = line.strip().split("اخفاء")[0].strip()
            if line in exclude or len(line) < 5: continue
            if any(k in line for k in ["لائحة", "نظام", "اللوائح"]): found.append(line)
        meta.related_regulations = list(dict.fromkeys(found))

    return meta

def parse_legal_text(text: str, meta: ArticleMetadata) -> List[dict]:
    articles = []
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    cur_part = cur_ch = cur_num = None
    buf = []

    def flush():
        nonlocal cur_num, buf
        if cur_num and buf:
            idx = arabic_ordinal_to_int(cur_num)
            clean_sys_id = meta.system_name.replace(" ", "_")
            articles.append({
                "chunk_id": f"{clean_sys_id}_Art_{idx}",
                "hierarchy": {"part": cur_part, "chapter": cur_ch, "article_number": f"المادة {cur_num}", "article_index": idx},
                "content": {"text": "\n".join(buf).strip()}
            })
            buf = []

    for line in lines:
        if line.startswith("الباب"): flush(); cur_part = line; cur_num = None
        elif line.startswith("الفصل"): flush(); cur_ch = line; cur_num = None
        elif line.startswith("المادة"): 
            flush()
            cur_num = line.replace("المادة", "").strip()
        elif cur_num and not any(x in line for x in ["النص الأصلي", "تاريخ النشر", "التصنيف", "وثيقة", "أداة إصدار"]):
            if line != meta.system_name: buf.append(line)
    flush()
    return articles

def main():
    print("⚖️ Watheq Bundler V9 - Final Fixes")
    input_lines = []
    while True:
        try:
            line = input()
            if line.strip().lower() in ['done', 'تم']: break
            input_lines.append(line)
        except EOFError: break
    
    full_text = "\n".join(input_lines)
    meta = extract_metadata_from_text(full_text)
    articles = parse_legal_text(full_text, meta)
    
    output_dir = Path("output_chunks")
    output_dir.mkdir(exist_ok=True)
    
    safe_filename = meta.system_name.replace(" ", "_") + ".json"
    file_path = output_dir / safe_filename
    
    output = {"system_info": asdict(meta), "articles": articles}
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ تم الحفظ بنجاح في: {file_path}")

if __name__ == "__main__":
    main()