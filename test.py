import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("LITELLM_KEY"),
    base_url=os.getenv("LITELLM_BASE_URL")
)

conversation = [
    {
        "role": "system",
        "content": "تحدث دائمًا باللهجة السعودية وبأسلوب طبيعي."
    }
]

print("ابدأ المحادثة. اكتب exit للخروج.\n")

while True:
    user_input = input("أنت: ")

    if user_input.lower() in ["exit", "quit"]:
        print("تم إنهاء المحادثة.")
        break

    conversation.append(
        {"role": "user", "content": user_input}
    )

    try:
        response = client.chat.completions.create(
            model="nuha-2.0",
            messages=conversation
        )

        assistant_reply = response.choices[0].message.content

        print(f"\nالمساعد: {assistant_reply}\n")

        conversation.append(
            {"role": "assistant", "content": assistant_reply}
        )

    except Exception as e:
        print(f"\nحدث خطأ: {e}\n")