"""Lists the Gemini models available for the configured API key.

Model availability depends on the account/tier/region, so querying the API
directly is more reliable than trusting hardcoded model names.

Usage (from the backend root, with the venv active):
    python scripts/list_gemini_models.py
"""

from google import genai

from app.core.config import settings


def main():
    if not settings.GEMINI_API_KEY:
        print("GEMINI_API_KEY is not set in .env")
        return

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    print("Models available for this key (support generateContent):\n")
    for model in client.models.list():
        actions = getattr(model, "supported_actions", None) or []
        if not actions or "generateContent" in actions:
            print(f"  {model.name}")

    print("\nFull list (including embedding/image/etc. models):\n")
    for model in client.models.list():
        print(f"  {model.name}  |  actions={getattr(model, 'supported_actions', None)}")


if __name__ == "__main__":
    main()
