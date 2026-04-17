import streamlit as st
import fitz  # PyMuPDF
from rag import RAGPipeline
from rag_contract import ContractRAG
# -------------------------
# INIT
# -------------------------
contract_rag = ContractRAG()
rag = RAGPipeline()

st.set_page_config(
    page_title="Watheq Legal AI",
    page_icon="⚖️",
    layout="wide"
)

# -------------------------
# PDF TEXT EXTRACTION
# -------------------------
def extract_pdf_text(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")

    full_text = ""

    for page in doc:
        full_text += page.get_text("text") + "\n"

    return full_text.strip()

# -------------------------
# UI HEADER
# -------------------------
st.title("⚖️ Watheq Legal AI")
st.markdown("Legal assistant + contract compliance analyzer for Saudi laws")

# -------------------------
# SESSION STATE
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------
# MODE SELECT
# -------------------------
mode = st.sidebar.selectbox(
    "Choose Mode",
    ["💬 Chat Assistant", "📄 Contract Compliance Analysis"]
)

# =========================================================
# 💬 CHAT MODE
# =========================================================

if mode == "💬 Chat Assistant":

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask a legal question...")

    if user_input:

        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Searching legal database... ⚖️"):

                result = rag.answer(user_input)

                st.markdown(result["answer"])

                with st.expander("📚 Retrieved Sources"):
                    for i, src in enumerate(result["sources"]):
                        st.markdown(f"**Source {i+1}**")
                        st.write(src["text"])
                        st.markdown("---")

        st.session_state.messages.append(
            {"role": "assistant", "content": result["answer"]}
        )

# =========================================================
# 📄 CONTRACT COMPLIANCE MODE (JSON OUTPUT)
# =========================================================
elif mode == "📄 Contract Compliance Analysis":

    st.subheader("📄 Upload Contract PDF")

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_file:

        text = extract_pdf_text(uploaded_file)

        st.subheader("📄 Extracted Contract")
        st.text_area("Contract Text", text, height=300)

        # -------------------------
        # EXACT PROMPT YOU PROVIDED
        # -------------------------
        prompt = f"""
أنت محلل قانوني متخصص في مراجعة العقود وفق الأنظمة السعودية.
مهمتك تحليل الملف المقدم ومقارنته بالنصوص النظامية المسترجعة للكشف عن المخاطر القانونية.

أجب فقط بـ JSON صالح بالهيكل التالي بدون أي نص إضافي أو markdown:
{{
  "contractTitle": "عنوان العقد",
  "complianceScore": 0-100,
  "summary": {{ "high": 0, "medium": 0, "low": 0 }},
  "issues": [
    {{
      "id": 1,
      "title": "عنوان المشكلة",
      "riskLevel": "عالية | متوسطة | منخفضة",
      "reason": "سبب المخالفة النظامية",
      "recommendation": "كيفية التصحيح",
      "legalReference": "اسم النظام - المادة XX",
      "articleText": "النص الحرفي من الأنظمة"
    }}
  ]
}}

قواعد صارمة:
- لا تذكر أي معلومات خارج النصوص النظامية الموجودة
- complianceScore يعكس مدى الامتثال (100 = امتثال كامل, 0 = مخالفة كاملة) يكون حساب النسبة عن طريقة مقارنة عدد المخاطر بكامل البنود في العقد
- حدد فقط المشاكل التي لها أساس نظامي صريح

العقد:
{text}
"""

        if st.button("Analyze Contract ⚖️"):

            with st.spinner("Analyzing compliance... ⚖️"):

                result = contract_rag.answer(prompt)

                st.subheader("📊 Compliance Result (Raw Output)")

                st.code(result["answer"], language="json")

                with st.expander("📚 Retrieved Legal Sources"):
                    for i, src in enumerate(result["sources"]):
                        st.markdown(f"**Source {i+1}**")
                        st.write(src["text"])
                        st.markdown("---")