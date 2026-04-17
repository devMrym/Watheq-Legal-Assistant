from litellm import completion
import os
from dotenv import load_dotenv

load_dotenv()


class LegalLLM:

    # =========================
    # 💬 CHAT MODE
    # =========================
    def generate_chat_answer(self, question, docs):

        context = "\n\n".join([d["text"] for d in docs])

        prompt = f"""أنت واثق، مساعد قانوني متخصص في الأنظمة السعودية. 
مهمتك الوحيدة هي الإجابة بناءً على النصوص النظامية المسترجعة المقدمة لك فحسب.

القواعد الصارمة:
1. لا تستخدم أبداً عبارات مثل "بناءً على معرفتي العامة" أو "في القانون العام"
2. إجاباتك تقتصر حصراً على ما تجده في النصوص النظامية المقدمة
3. إذا لم تجد نصاً صريحاً، أجب بالضبط: "لا يوجد نص نظامي صريح يغطي هذه الحالة ضمن الأنظمة المتوفرة."
4. استشهد بالمادة والنظام دائماً
5. اكتب الإجابة بشكل هيكلي واضح

صيغة الإجابة:
**الإجابة المختصرة:** [إجابة موجزة]

**الأساس النظامي:** [النص الحرفي للمادة المستشهد بها]

**التوضيح:** [كيف تنطبق المادة على الحالة]

**المصدر:** [اسم النظام - رقم المادة]
    
Question:
{question}

Legal Context:
{context}
"""

        response = completion(
            model="openai/nuha-2.0",   # IMPORTANT FIX
            api_key=os.getenv("NUHA_API_KEY"),
            api_base=os.getenv("NUHA_BASE_URL"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        return response["choices"][0]["message"]["content"]

    # =========================
    # 📄 CONTRACT MODE
    # =========================
    def generate_contract_answer(self, contract_text, docs):

        context = "\n\n".join([d["text"] for d in docs])

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
{contract_text}
"""


        response = completion(
            model="openai/nuha-2.0",   # IMPORTANT FIX
            api_key=os.getenv("NUHA_API_KEY"),
            api_base=os.getenv("NUHA_BASE_URL"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

        return response["choices"][0]["message"]["content"]