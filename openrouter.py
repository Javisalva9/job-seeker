import os
import openai

# Get OpenRouter API key (already loaded in main.py)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("❌ Missing OpenRouter API key! Set it in a .env file.")

def ask_openrouter(prompt, model="qwen/QwQ-32B-Preview"):
    """
    Sends a request to OpenRouter's API using the specified model.

    :param prompt: The text prompt to send.
    :param model: The AI model to use (default: Qwen QwQ-32B-Preview).
    :return: The AI response as a string.
    """
    try:
        client = openai.OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ OpenRouter Error: {e}")
        return None
