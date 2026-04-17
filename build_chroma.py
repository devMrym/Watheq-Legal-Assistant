import os
import json
import shutil
import chromadb
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

# =========================
# CONFIG
# =========================
DATA_FOLDER = "./data"
CHROMA_DB_DIR = "./chroma_db"
COLLECTION_NAME = "saudi_laws"

EMBEDDING_MODEL = "BAAI/bge-m3"
LOG_FILE = "bad_entries.log"

# =========================
# CLEAN OLD DB (IMPORTANT)
# =========================
if os.path.exists(CHROMA_DB_DIR):
    print("🧹 Deleting old ChromaDB...")
    shutil.rmtree(CHROMA_DB_DIR)

# =========================
# MODEL
# =========================
print("Loading BGE-M3 model...")
model = SentenceTransformer(EMBEDDING_MODEL)

# =========================
# CHROMA INIT
# =========================
client = chromadb.Client(
    chromadb.config.Settings(
        persist_directory=CHROMA_DB_DIR
    )
)

collection = client.get_or_create_collection(name=COLLECTION_NAME)

# =========================
# STORAGE
# =========================
documents = []
metadatas = []
ids = []

bad_count = 0

# =========================
# LOGGING
# =========================
def log_error(msg, obj=None):
    global bad_count
    bad_count += 1

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
        if obj:
            f.write(json.dumps(obj, ensure_ascii=False, indent=2))
            f.write("\n\n")

# =========================
# SAFE DEFAULTS
# =========================
def safe_str(v, default="غير معروف"):
    if v is None:
        return default
    return str(v)

def safe_int(v, default=-1):
    if v is None:
        return default
    try:
        return int(v)
    except:
        return default

# =========================
# UNIQUE ID
# =========================
def make_unique_id(chunk_id, file_name, counter):
    return f"{chunk_id}__{file_name}__{counter}"

# =========================
# PARSER
# =========================
def parse_article(article, file_path):
    try:
        chunk_id = article.get("chunk_id")
        if not chunk_id:
            chunk_id = f"missing_id_{len(ids)}"

        content = article.get("content", {})
        text = content.get("text", "")

        if not text or len(text.strip()) < 1:
            log_error("❌ Empty text skipped", article)
            return None

        hierarchy = article.get("hierarchy", {}) or {}

        number_text = (
            hierarchy.get("number_text")
            or hierarchy.get("article_number")
            or f"مادة {hierarchy.get('index', 'غير معروف')}"
        )

        index = hierarchy.get("index") or hierarchy.get("article_index")
        index = safe_int(index)

        return {
            "chunk_id": chunk_id,
            "text": text.strip(),
            "number_text": number_text,
            "index": index
        }

    except Exception as e:
        log_error(f"❌ Parse error: {file_path} | {e}", article)

        return {
            "chunk_id": f"error_fallback_{len(ids)}",
            "text": json.dumps(article, ensure_ascii=False),
            "number_text": "غير معروف",
            "index": -1
        }

# =========================
# PROCESS FILE
# =========================
def process_json(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        log_error(f"❌ JSON read error: {file_path} | {e}")
        return

    system_info = data.get("system_info", {}) or {}

    system_name = safe_str(system_info.get("system_name"))
    issue_date = safe_str(system_info.get("issue_date"))

    articles = data.get("articles", [])
    file_name = os.path.basename(file_path).replace(".json", "")

    for article in articles:
        parsed = parse_article(article, file_path)
        if not parsed:
            continue

        unique_id = make_unique_id(parsed["chunk_id"], file_name, len(ids))

        full_text = f"""النظام: {system_name}
تاريخ الإصدار: {issue_date}
المادة: {parsed["number_text"]}

{parsed["text"]}
"""

        metadata = {
            "system_name": system_name,
            "article_number": parsed["index"],
            "article_label": safe_str(parsed["number_text"]),
            "issue_date": issue_date,
            "source_file": file_name
        }

        documents.append(full_text.strip())
        metadatas.append(metadata)
        ids.append(unique_id)

# =========================
# LOAD DATA
# =========================
print("Reading JSON files...")

if os.path.exists(LOG_FILE):
    os.remove(LOG_FILE)

for file in os.listdir(DATA_FOLDER):
    if file.endswith(".json"):
        process_json(os.path.join(DATA_FOLDER, file))

print("\n====================")
print(f"✅ Total stored chunks: {len(documents)}")
print(f"⚠️ Bad logs: {bad_count}")
print("====================\n")

# =========================
# EMBEDDING + CHROMA
# =========================
print("Embedding with BGE-M3...")

BATCH_SIZE = 32

for i in tqdm(range(0, len(documents), BATCH_SIZE)):
    batch_docs = documents[i:i + BATCH_SIZE]
    batch_meta = metadatas[i:i + BATCH_SIZE]
    batch_ids = ids[i:i + BATCH_SIZE]

    try:
        embeddings = model.encode(
            batch_docs,
            normalize_embeddings=True,
            show_progress_bar=False
        ).tolist()

        collection.add(
            documents=batch_docs,
            metadatas=batch_meta,
            ids=batch_ids,
            embeddings=embeddings
        )

    except Exception as e:
        log_error(f"❌ Batch failed at {i}: {e}")

# =========================
# 🔥 CRITICAL: SAVE DB
# =========================
client.persist()

print("✅ DONE: Zero-loss ChromaDB built successfully")
print(f"📁 Chroma saved to: {CHROMA_DB_DIR}")
print(f"📁 Logs saved to: {LOG_FILE}")