#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚖️ Arabic Legal Text Chunker
Parses Saudi legal texts (أنظمة، لوائح، قواعد) into structured JSON chunks.
Usage: python legal_chunker.py
Paste text, then type 'done' on a new line and press Enter.
"""

import re
import json
import sys
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Tuple


# ══════════════════════════════════════════════════════════════════════════════
# Arabic Number Conversion
# ══════════════════════════════════════════════════════════════════════════════

ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

ORDINAL_MAP = {
    # Units
    "الأولى": 1, "الأول": 1, "الحادية": 1, "الحادي": 1,
    "الثانية": 2, "الثاني": 2,
    "الثالثة": 3, "الثالث": 3,
    "الرابعة": 4, "الرابع": 4,
    "الخامسة": 5, "الخامس": 5,
    "السادسة": 6, "السادس": 6,
    "السابعة": 7, "السابع": 7,
    "الثامنة": 8, "الثامن": 8,
    "التاسعة": 9, "التاسع": 9,
    "العاشرة": 10, "العاشر": 10,
    # Teens
    "الحادية عشرة": 11, "الحادي عشر": 11,
    "الثانية عشرة": 12, "الثاني عشر": 12,
    "الثالثة عشرة": 13, "الثالث عشر": 13,
    "الرابعة عشرة": 14, "الرابع عشر": 14,
    "الخامسة عشرة": 15, "الخامس عشر": 15,
    "السادسة عشرة": 16, "السادس عشر": 16,
    "السابعة عشرة": 17, "السابع عشر": 17,
    "الثامنة عشرة": 18, "الثامن عشر": 18,
    "التاسعة عشرة": 19, "التاسع عشر": 19,
    # Tens
    "العشرون": 20, "العشرين": 20,
    "الحادية والعشرون": 21, "الحادي والعشرون": 21,
    "الثانية والعشرون": 22, "الثاني والعشرون": 22,
    "الثالثة والعشرون": 23, "الثالث والعشرون": 23,
    "الرابعة والعشرون": 24, "الرابع والعشرون": 24,
    "الخامسة والعشرون": 25, "الخامس والعشرون": 25,
    "السادسة والعشرون": 26, "السادس والعشرون": 26,
    "السابعة والعشرون": 27, "السابع والعشرون": 27,
    "الثامنة والعشرون": 28, "الثامن والعشرون": 28,
    "التاسعة والعشرون": 29, "التاسع والعشرون": 29,
    "الثلاثون": 30, "الثلاثين": 30,
    "الحادية والثلاثون": 31, "الحادي والثلاثون": 31,
    "الثانية والثلاثون": 32, "الثاني والثلاثون": 32,
    "الثالثة والثلاثون": 33, "الثالث والثلاثون": 33,
    "الرابعة والثلاثون": 34, "الرابع والثلاثون": 34,
    "الخامسة والثلاثون": 35, "الخامس والثلاثون": 35,
    "السادسة والثلاثون": 36, "السادس والثلاثون": 36,
    "السابعة والثلاثون": 37, "السابع والثلاثون": 37,
    "الثامنة والثلاثون": 38, "الثامن والثلاثون": 38,
    "التاسعة والثلاثون": 39, "التاسع والثلاثون": 39,
    "الأربعون": 40, "الأربعين": 40,
    "الحادية والأربعون": 41, "الحادي والأربعون": 41,
    "الثانية والأربعون": 42, "الثاني والأربعون": 42,
    "الثالثة والأربعون": 43, "الثالث والأربعون": 43,
    "الرابعة والأربعون": 44, "الرابع والأربعون": 44,
    "الخامسة والأربعون": 45, "الخامس والأربعون": 45,
    "السادسة والأربعون": 46, "السادس والأربعون": 46,
    "السابعة والأربعون": 47, "السابع والأربعون": 47,
    "الثامنة والأربعون": 48, "الثامن والأربعون": 48,
    "التاسعة والأربعون": 49, "التاسع والأربعون": 49,
    "الخمسون": 50, "الخمسين": 50,
    "الحادية والخمسون": 51, "الحادي والخمسون": 51,
    "الثانية والخمسون": 52, "الثاني والخمسون": 52,
    "الثالثة والخمسون": 53, "الثالث والخمسون": 53,
    "الرابعة والخمسون": 54, "الرابع والخمسون": 54,
    "الخامسة والخمسون": 55, "الخامس والخمسون": 55,
    "السادسة والخمسون": 56, "السادس والخمسون": 56,
    "السابعة والخمسون": 57, "السابع والخمسون": 57,
    "الثامنة والخمسون": 58, "الثامن والخمسون": 58,
    "التاسعة والخمسون": 59, "التاسع والخمسون": 59,
    "الستون": 60, "الستين": 60,
    "الحادية والستون": 61, "الحادي والستون": 61,
    "الثانية والستون": 62, "الثاني والستون": 62,
    "الثالثة والستون": 63, "الثالث والستون": 63,
    "الرابعة والستون": 64, "الرابع والستون": 64,
    "الخامسة والستون": 65, "الخامس والستون": 65,
    "السادسة والستون": 66, "السادس والستون": 66,
    "السابعة والستون": 67, "السابع والستون": 67,
    "الثامنة والستون": 68, "الثامن والستون": 68,
    "التاسعة والستون": 69, "التاسع والستون": 69,
    "السبعون": 70, "السبعين": 70,
    "الحادية والسبعون": 71, "الحادي والسبعون": 71,
    "الثانية والسبعون": 72, "الثاني والسبعون": 72,
    "الثالثة والسبعون": 73, "الثالث والسبعون": 73,
    "الرابعة والسبعون": 74, "الرابع والسبعون": 74,
    "الخامسة والسبعون": 75, "الخامس والسبعون": 75,
    "السادسة والسبعون": 76, "السادس والسبعون": 76,
    "السابعة والسبعون": 77, "السابع والسبعون": 77,
    "الثامنة والسبعون": 78, "الثامن والسبعون": 78,
    "التاسعة والسبعون": 79, "التاسع والسبعون": 79,
    "الثمانون": 80, "الثمانين": 80,
    "الحادية والثمانون": 81, "الحادي والثمانون": 81,
    "الثانية والثمانون": 82, "الثاني والثمانون": 82,
    "الثالثة والثمانون": 83, "الثالث والثمانون": 83,
    "الرابعة والثمانون": 84, "الرابع والثمانون": 84,
    "الخامسة والثمانون": 85, "الخامس والثمانون": 85,
    "السادسة والثمانون": 86, "السادس والثمانون": 86,
    "السابعة والثمانون": 87, "السابع والثمانون": 87,
    "الثامنة والثمانون": 88, "الثامن والثمانون": 88,
    "التاسعة والثمانون": 89, "التاسع والثمانون": 89,
    "التسعون": 90, "التسعين": 90,
    "الحادية والتسعون": 91, "الحادي والتسعون": 91,
    "الثانية والتسعون": 92, "الثاني والتسعون": 92,
    "الثالثة والتسعون": 93, "الثالث والتسعون": 93,
    "الرابعة والتسعون": 94, "الرابع والتسعون": 94,
    "الخامسة والتسعون": 95, "الخامس والتسعون": 95,
    "السادسة والتسعون": 96, "السادس والتسعون": 96,
    "السابعة والتسعون": 97, "السابع والتسعون": 97,
    "الثامنة والتسعون": 98, "الثامن والتسعون": 98,
    "التاسعة والتسعون": 99, "التاسع والتسعون": 99,
    "المائة": 100, "المئة": 100,
}


def arabic_ordinal_to_int(text: str) -> int:
    """Convert Arabic ordinal word or digit string to integer."""
    text = text.strip().translate(ARABIC_DIGITS)

    # Direct digit match
    num_match = re.search(r'\d+', text)
    if num_match:
        return int(num_match.group())

    # Try longest match from ORDINAL_MAP
    best_val = 0
    best_len = 0
    for word, val in ORDINAL_MAP.items():
        if word in text and len(word) > best_len:
            best_val = val
            best_len = len(word)

    return best_val if best_val else 0


# ══════════════════════════════════════════════════════════════════════════════
# Metadata Extraction
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class SystemMetadata:
    system_name: str = "غير محدد"
    issue_date: str = "غير محدد"
    publish_date: str = "غير محدد"
    issuing_decree: str = "غير محدد"
    last_update_decree: str = ""
    last_update_date: str = ""
    related_regulations: List[str] = field(default_factory=list)


# Noise lines to skip in article body
NOISE_PATTERNS = [
    r"^النص الأصلي",
    r"^تفاصيل إضافة",
    r"^تاريخ النشر",
    r"^التصنيف",
    r"^نوع التشريع",
    r"^حالة التشريع",
    r"^أداة إصدار",
    r"^وثيقة أداة",
    r"^وثيقة التشريع",
    r"^مرفق أداة",
    r"^اخفاء جدول",
    r"^رابط",
    r"^آخر تعديل$",
    r"^مضافة$",
    r"^ملغاة$",
]
NOISE_RE = re.compile("|".join(NOISE_PATTERNS))

# Structural keywords that are NOT article content
STRUCTURAL_KEYWORDS = ["الباب", "الفصل", "القسم", "الفرع", "الجزء"]


def is_structural(line: str) -> bool:
    return any(line.startswith(kw) for kw in STRUCTURAL_KEYWORDS)


def is_article_header(line: str) -> Tuple[bool, str]:
    """Check if line is an article header. Returns (is_header, ordinal_text)."""
    # Pattern: المادة + ordinal
    m = re.match(r'^المادة\s+(.+)', line)
    if m:
        return True, m.group(1).strip()
    return False, ""


def clean_meta_value(val: str) -> str:
    """Strip noise from extracted metadata values."""
    noise = ["التصنيف", "نوع التشريع", "تاريخ النشر", "حالة التشريع",
             "أداة", "وثيقة", "مرفق", "اخفاء", "رابط"]
    for n in noise:
        if n in val:
            val = val.split(n)[0]
    return val.strip().split('\n')[0].strip()


def detect_system_name(lines: List[str]) -> str:
    """
    Try multiple strategies to extract the system/regulation name.
    """
    candidates = []

    for i, line in enumerate(lines):
        # Strategy 1: line before "الباب الأول"
        if "الباب الأول" in line and i > 0:
            prev = lines[i - 1].strip()
            if len(prev) > 5 and len(prev) < 120:
                candidates.append((prev, 10))

        # Strategy 2: line that starts with نظام / لائحة / قواعد / ضوابط / آلية
        if re.match(r'^(نظام|لائحة|قواعد|ضوابط|آلية|تنظيم)\s+', line) and len(line) < 120:
            candidates.append((line, 8))

        # Strategy 3: line ending with ".pdf" stripped
        if line.endswith('.pdf'):
            name = line.replace('.pdf', '').strip()
            candidates.append((name, 7))

    if candidates:
        # Sort by score descending, then pick first
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]

    return "غير محدد"


def extract_metadata(text: str) -> SystemMetadata:
    meta = SystemMetadata()
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    meta.system_name = detect_system_name(lines)

    # Date / decree patterns
    patterns = {
        "issue_date": r"تاريخ الاصدار\s*\n?([\u0600-\u06FF\d\s/]+)",
        "publish_date": r"تاريخ النشر\s*\n?([\u0600-\u06FF\d\s/]+)",
        "last_update_decree": r"أداة إصدار آخر تحديث\s*\n?([^\n]+)",
        "last_update_date": r"تاريخ أداة آخر تحديث\s*\n?([\u0600-\u06FF\d\s/]+)",
    }

    for key, pattern in patterns.items():
        m = re.search(pattern, text, re.M)
        if m:
            setattr(meta, key, clean_meta_value(m.group(1)))

    # Issuing decree — multiple attempts
    decree_patterns = [
        r"أداة إصدار نظام[^\n]*\n(المرسوم الملكي[^\n]+|قرار[^\n]+|م/[^\n]+)",
        r"إصدار آخر تحديث\s*\n?(المرسوم الملكي[^\n]+|قرار[^\n]+)",
        r"(المرسوم الملكي رقم \([^)]+\)[^\n]*)",
        r"الصادر بالمرسوم الملكي رقم ([^\n]+)",
    ]
    for pat in decree_patterns:
        m = re.search(pat, text, re.M)
        if m:
            val = clean_meta_value(m.group(1))
            if val and "آخر تحديث" not in val:
                meta.issuing_decree = val
                break

    # Related regulations block
    reg_m = re.search(r"التشريعات المرتبطة(.*?)(?:المادة الأولى|$)", text, re.S)
    if reg_m:
        block = reg_m.group(1)
        exclude = {meta.system_name, "التشريعات المرتبطة",
                   "النظام المرتبط باللائحة", "اللائحة المرتبطة بالنظام"}
        found = []
        for ln in block.splitlines():
            ln = ln.strip().split("اخفاء")[0].strip()
            if not ln or ln in exclude or len(ln) < 5:
                continue
            if any(k in ln for k in ["لائحة", "نظام", "اللوائح", "قواعد", "ضوابط", "دليل"]):
                found.append(ln)
        meta.related_regulations = list(dict.fromkeys(found))

    return meta


# ══════════════════════════════════════════════════════════════════════════════
# Article Parsing
# ══════════════════════════════════════════════════════════════════════════════

def parse_articles(text: str, meta: SystemMetadata) -> List[dict]:
    articles = []
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    cur_part: Optional[str] = None
    cur_chapter: Optional[str] = None
    cur_section: Optional[str] = None  # قسم / فرع
    cur_art_ordinal: Optional[str] = None
    cur_art_num: Optional[str] = None   # raw header text e.g. "الأولى"
    buf: List[str] = []

    def flush():
        nonlocal buf, cur_art_ordinal, cur_art_num
        if cur_art_ordinal and buf:
            idx = arabic_ordinal_to_int(cur_art_ordinal)
            safe_name = meta.system_name.replace(" ", "_").replace("/", "-")
            article = {
                "chunk_id": f"{safe_name}_Art_{idx}",
                "hierarchy": {
                    "part": cur_part,
                    "chapter": cur_chapter,
                    "section": cur_section,
                    "article_number": f"المادة {cur_art_ordinal}",
                    "article_index": idx,
                },
                "content": {
                    "text": "\n".join(buf).strip()
                }
            }
            articles.append(article)
        buf = []

    for line in lines:
        # Skip noise lines
        if NOISE_RE.match(line):
            continue

        # Skip lines that are just the system name repeated
        if line == meta.system_name:
            continue

        # Structural headers
        if line.startswith("الباب"):
            flush()
            cur_part = line
            cur_chapter = None
            cur_section = None
            cur_art_ordinal = None
            continue

        if line.startswith("الفصل"):
            flush()
            cur_chapter = line
            cur_section = None
            cur_art_ordinal = None
            continue

        if line.startswith("القسم") or line.startswith("الفرع") or line.startswith("الجزء"):
            flush()
            cur_section = line
            cur_art_ordinal = None
            continue

        # Article header
        is_art, ordinal_text = is_article_header(line)
        if is_art:
            flush()
            cur_art_ordinal = ordinal_text
            cur_art_num = line
            continue

        # Content line — only accumulate if inside an article
        if cur_art_ordinal is not None:
            # Skip very long metadata lines that sneak in
            if any(kw in line for kw in [
                "تاريخ الاصدار", "أداة إصدار", "وثيقة التشريع",
                "مرفق أداة", "اخفاء جدول المحتوى",
            ]):
                continue
            buf.append(line)

    flush()
    return articles


# ══════════════════════════════════════════════════════════════════════════════
# Deduplication & Validation
# ══════════════════════════════════════════════════════════════════════════════

def deduplicate_articles(articles: List[dict]) -> List[dict]:
    """
    If two articles share the same index, merge their content
    (handles split articles like 'مضافة', 'آخر تعديل' variants).
    """
    seen = {}
    for art in articles:
        idx = art["hierarchy"]["article_index"]
        if idx not in seen:
            seen[idx] = art
        else:
            # Append the extra content
            existing_text = seen[idx]["content"]["text"]
            new_text = art["content"]["text"]
            if new_text and new_text not in existing_text:
                seen[idx]["content"]["text"] = existing_text + "\n\n" + new_text

    # Sort by article index
    result = sorted(seen.values(), key=lambda a: a["hierarchy"]["article_index"])
    return result


# ══════════════════════════════════════════════════════════════════════════════
# Output
# ══════════════════════════════════════════════════════════════════════════════

def save_output(meta: SystemMetadata, articles: List[dict]) -> Path:
    output_dir = Path("output_chunks")
    output_dir.mkdir(exist_ok=True)

    safe_name = re.sub(r'[^\w\u0600-\u06FF]', '_', meta.system_name)
    file_path = output_dir / f"{safe_name}.json"

    output = {
        "system_info": asdict(meta),
        "articles": articles
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    return file_path


# ══════════════════════════════════════════════════════════════════════════════
# Main Interactive Loop
# ══════════════════════════════════════════════════════════════════════════════

BANNER = """
╔══════════════════════════════════════════════════════════╗
║         ⚖️  Arabic Legal Text Chunker  ⚖️                ║
║    محلل النصوص القانونية العربية إلى مقاطع منظمة         ║
╚══════════════════════════════════════════════════════════╝

الاستخدام:
  • الصق النص القانوني كاملاً
  • اكتب  done  أو  تم  في سطر منفرد ثم اضغط Enter

"""


def main():
    print(BANNER)

    while True:
        print("─" * 60)
        print("📋 الصق النص هنا (أو اكتب 'خروج' للإنهاء):")
        print("─" * 60)

        input_lines = []
        while True:
            try:
                line = input()
            except EOFError:
                break

            if line.strip().lower() in ("done", "تم"):
                break
            if line.strip() in ("خروج", "exit", "quit"):
                print("\n👋 إلى اللقاء!")
                sys.exit(0)

            input_lines.append(line)

        if not input_lines:
            print("⚠️  لم يتم إدخال أي نص. حاول مجدداً.\n")
            continue

        full_text = "\n".join(input_lines)

        print("\n🔍 جاري التحليل...\n")

        # Extract
        meta = extract_metadata(full_text)
        articles = parse_articles(full_text, meta)
        articles = deduplicate_articles(articles)

        # Stats
        if not articles:
            print("❌ لم يتم العثور على أي مادة. تأكد أن النص يحتوي على 'المادة ...'")
            continue

        print(f"📌 اسم النظام   : {meta.system_name}")
        print(f"📅 تاريخ الإصدار : {meta.issue_date}")
        print(f"📜 أداة الإصدار  : {meta.issuing_decree}")
        print(f"🔄 آخر تحديث    : {meta.last_update_decree or 'لا يوجد'}")
        print(f"📎 التشريعات المرتبطة: {len(meta.related_regulations)}")
        print(f"📑 عدد المواد   : {len(articles)}")

        if articles:
            indices = [a["hierarchy"]["article_index"] for a in articles]
            print(f"   من المادة {min(indices)} إلى المادة {max(indices)}")

        # Save
        out_path = save_output(meta, articles)
        print(f"\n✅ تم الحفظ في: {out_path}")

        # Preview first article
        if articles:
            print("\n── معاينة المادة الأولى ──")
            first = articles[0]
            preview_text = first["content"]["text"]
            if len(preview_text) > 300:
                preview_text = preview_text[:300] + "..."
            print(f"  {first['chunk_id']}")
            print(f"  الباب : {first['hierarchy']['part']}")
            print(f"  الفصل : {first['hierarchy']['chapter']}")
            print(f"  النص  : {preview_text}")

        print("\n" + "═" * 60)
        print("هل تريد تحليل نص آخر؟ (اضغط Enter للمتابعة أو اكتب 'خروج')")
        try:
            again = input().strip()
        except EOFError:
            again = "خروج"
        if again in ("خروج", "exit", "quit"):
            print("\n👋 إلى اللقاء!")
            break
        print()


if __name__ == "__main__":
    main()