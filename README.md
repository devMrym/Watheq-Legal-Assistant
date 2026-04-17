# ⚖️ Watheq - واثق (Legal AI)

An advanced AI-powered platform for Saudi Arabian law, featuring a specialized Legal Chat Assistant and a Document Compliance Analyzer. Built specifically to align with the Kingdom's regulations and legal frameworks.

---

## 🌟 Core Modules

### 💬 1. Legal Chat Assistant

A dedicated chat interface that allows users to inquire about any Saudi law.

- **Regulatory Knowledge:** Powered by a RAG (Retrieval-Augmented Generation) pipeline containing Saudi legal codes.
- **Verifiable Answers:** Every response includes the specific Article Number and Law Name for legal grounding.
- **Contextual Understanding:** Handles complex legal queries with high accuracy using the Nuha-2.0 LLM.

---

### 📄 2. Document Compliance Analyzer

A specialized tool for uploading and auditing legal documents or contracts.

- **Automated Auditing:** Compares uploaded PDFs against current Saudi regulations.
- **Risk Categorization:** Flags potential legal gaps as High, Medium, or Low risk.
- **Corrective Guidance:** Provides actionable recommendations and the exact legal text required to fix each issue.
- **Arabic Precision:** Uses PyMuPDF for high-fidelity Arabic text extraction, ensuring no letter flipping or encoding errors.

---

## 🛠️ Tech Stack

- Frontend: React, Tailwind CSS, Framer Motion (Modern, RTL-first UI)
- Backend: FastAPI (Python), PyMuPDF (Fitz)
- Vector Database: ChromaDB (BGE-M3 Embeddings)
- LLM: Nuha-2.0 (Specialized Arabic Legal Model) via LiteLLM

---

## 📦 Installation & Setup

### 1. Backend Setup (Root Directory)

Ensure you have Python 3.10+ installed.

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a .env file in the root directory:

```env
NUHA_API_KEY=your_key_here
NUHA_BASE_URL=your_base_url
```

Start the API server, Open the terminal and run this command and keep it running:

```bash
uvicorn api:app --reload  
```

---

### 2. Frontend Setup

In a second Terminal, Navigate to the Watheq-website folder:

```bash
cd Watheq-website
```

Install packages:

```bash
npm install
```

Launch the development server:

```bash
npm run dev
```

---

## 🛡️ Arabic Support Note

This project implements unicode-bidi: plaintext and PyMuPDF extraction to solve the common "reversed text" issue in Arabic PDF processing. This ensures correct Arabic rendering.


---

## 👥 Contact Us
Maryam Alonazi: mrym.alonazi@gmail.com
Ashwaq Almutairi: ashwag1cs@gmail.com

