from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag import RAGPipeline
import fitz  # PyMuPDF replaces pdfplumber
import tempfile
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = RAGPipeline()

@app.post("/upload-contract")
async def upload_contract(file: UploadFile = File(...)):
    # 1. Save temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # 2. Extract text using fitz (PyMuPDF) - identical to your Streamlit logic
    text = ""
    try:
        doc = fitz.open(tmp_path)
        for page in doc:
            # "text" mode in fitz usually handles Arabic better than pdfplumber
            text += page.get_text("text") + "\n"
        doc.close()
    except Exception as e:
        return {"error": str(e)}
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    # 3. Process with RAG
    result = rag.answer(text, mode="contract")

    # Ensure the original text is sent back to React for the display
    # so the user sees exactly what was extracted.
    if isinstance(result, dict):
        result["question"] = text.strip()

    return result