# ⚖️ Watheq Legal AI Analyzer

An advanced legal assistant and contract compliance analyzer specifically designed for **Saudi Arabian Laws and Regulations**.

## 🚀 Features
* **Contract Analysis:** Upload PDF contracts to check compliance with Saudi laws.
* **Risk Assessment:** Categorizes issues into High, Medium, and Low risks.
* **Arabic Support:** Full RTL support with correct character reshaping using PyMuPDF.
* **Legal RAG:** Powered by the Nuha LLM for high-accuracy legal citations.

## 🛠️ Tech Stack
* **Frontend:** React, Tailwind CSS, Framer Motion, Lucide React.
* **Backend:** FastAPI (Python), PyMuPDF (Fitz).
* **LLM:** Nuha-2.0 via LiteLLM.

## 📦 Installation

### Backend
1. `cd backend`
2. `pip install -r requirements.txt`
3. Create a `.env` file with your `NUHA_API_KEY`.
4. `uvicorn main:app --reload`

### Frontend
1. `cd frontend`
2. `npm install`
3. `npm run dev`