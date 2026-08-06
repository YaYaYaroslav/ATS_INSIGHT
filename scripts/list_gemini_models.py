"""
Діагностичний скрипт: показує, які моделі Gemini доступні саме для твого
API-ключа (список моделей залежить від акаунта/тарифу/регіону, тому
надійніше спитати API напряму, ніж покладатись на назви з документації).

Запуск (з кореня backend-проєкту, з активованим venv):

    python3 -m scripts.list_gemini_models

Або напряму:

    python3 scripts/list_gemini_models.py
"""

from google import genai

from app.core.config import settings


def main():
    if not settings.GEMINI_API_KEY:
        print("GEMINI_API_KEY не задано в .env")
        return

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    print("Моделі, доступні для цього ключа (підтримують generateContent):\n")
    for model in client.models.list():
        actions = getattr(model, "supported_actions", None) or []
        if not actions or "generateContent" in actions:
            print(f"  {model.name}")

    print("\nПовний список (включно з embedding/image/etc моделями):\n")
    for model in client.models.list():
        print(f"  {model.name}  |  actions={getattr(model, 'supported_actions', None)}")


if __name__ == "__main__":
    main()
