from vectorstore import VectorStore
from llm import LegalLLM
from embedder import get_embedding

class RAGPipeline:
    def __init__(self):
        self.vectorstore = VectorStore()
        self.llm = LegalLLM()

    def answer(self, input_text: str, mode="chat"):

        # =========================
        # 1. INPUT HANDLING
        # =========================
        query_text = input_text

        # =========================
        # 2. EMBEDDING
        # =========================
        query_embedding = get_embedding(query_text, is_query=True)

        # =========================
        # 3. RETRIEVAL
        # =========================
        docs = self.vectorstore.search(query_embedding, top_k=20)

        # =========================
        # 4. CONTRACT FILTERING (ONLY IF CONTRACT MODE)
        # =========================
        if mode == "contract":
            filtered = []

            for d in docs:
                law_name = d.get("law_name", "")

                if "عمل" in law_name or "العمل" in law_name or law_name == "":
                    filtered.append(d)

            if len(filtered) > 5:
                docs = filtered

        # =========================
        # 5. REMOVE DUPLICATES
        # =========================
        seen = set()
        unique_docs = []

        for d in docs:
            text = d.get("text", "")
            if text not in seen:
                seen.add(text)
                unique_docs.append(d)

        # =========================
        # 6. BOOSTING (UNCHANGED LOGIC)
        # =========================
        for doc in unique_docs:
            doc["boost_score"] = 0
            text = doc["text"]

            boost_keywords = [
                "مساعدة", "المحكمة المختصة", "طلب من المحكمة", "تعاون",
                "أجر", "راتب", "إجازة", "ساعات العمل", "فصل", "تعويض"
            ]

            for word in boost_keywords:
                if word in text:
                    doc["boost_score"] += 10

            if "تحكيم" in query_text and "تحكيم" in doc.get("law_name", ""):
                doc["boost_score"] += 5

        unique_docs.sort(key=lambda x: x["boost_score"], reverse=True)

        final_docs = unique_docs[:10]

        # =========================
        # 7. DEBUG
        # =========================
        print(f"\n--- MODE: {mode} ---")
        for d in final_docs:
            print(f"[{d.get('law_name','Unknown')}] - {d.get('article_number','??')}")

        # =========================
        # 8. LLM CALL (CLEAN & CORRECT)
        # =========================
        if mode == "contract":
            answer = self.llm.generate_contract_answer(input_text, final_docs)
        else:
            answer = self.llm.generate_chat_answer(input_text, final_docs)

        return {
            "question": input_text,
            "answer": answer,
            "sources": final_docs
        }