# rag_contract.py
from vectorstore import VectorStore
from llm import LegalLLM
from embedder import get_embedding

class ContractRAG:
    def __init__(self):
        self.vectorstore = VectorStore()
        self.llm = LegalLLM()

    def extract_contract(self, prompt):
        if "العقد:" in prompt:
            return prompt.split("العقد:")[-1]
        return prompt

    def answer(self, prompt: str):

        contract_text = self.extract_contract(prompt)

        query_embedding = get_embedding(contract_text, is_query=True)

        # 🔥 get more results
        docs = self.vectorstore.search(query_embedding, top_k=40)

        # 🔥 HARD FILTER: prioritize labor law
        labor_docs = [
            d for d in docs
            if "عمل" in d.get("law_name", "")
        ]

        if len(labor_docs) > 5:
            docs = labor_docs

        # remove duplicates
        seen = set()
        unique_docs = []
        for d in docs:
            if d["text"] not in seen:
                seen.add(d["text"])
                unique_docs.append(d)

        # 🔥 BOOST relevant employment concepts
        for doc in unique_docs:
            doc["score"] = 0
            text = doc["text"]

            keywords = [
                "أجر", "راتب", "إجازة", "فصل",
                "تعويض", "ساعات العمل", "عمل إضافي"
            ]

            for k in keywords:
                if k in text:
                    doc["score"] += 5

            if "عمل" in doc.get("law_name", ""):
                doc["score"] += 10

        unique_docs.sort(key=lambda x: x["score"], reverse=True)

        final_docs = unique_docs[:12]

        print("\n--- CONTRACT MODE ---")
        for d in final_docs:
            print(f"[{d.get('law_name')}] - مادة {d.get('article_number')}")

        answer = self.llm.generate_answer(prompt, final_docs)

        return {
            "answer": answer,
            "sources": final_docs
        }