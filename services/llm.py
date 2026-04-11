import requests
from core.config import NVIDIA_API_KEY

URL = "https://integrate.api.nvidia.com/v1/chat/completions"
REQUEST_TIMEOUT = 30

context_len = 12

system_prompt = """You are a Chemistry tutor.
    Rules:
    - Respond in Portuguese
    - Be concise
    - If out of scope: "Posso ajudar apenas com dúvidas de química."
    - Use line breaks or bullet points when helpful
    - When writing chemical equations, format them clearly (e.g., H2 + O2 → H2O)
    - Never invent chemical compounds or minerals
    - If unknown, say: "Não tenho certeza sobre isso"""

last_messages = []

def generate_response(message: str):
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Accept": "application/json"
    }
 
    # monta histórico
    messages = [
        {"role": "system", "content": system_prompt},
        *last_messages,
        {"role": "user", "content": message}
    ]

    payload = {
        "model": "mistralai/ministral-14b-instruct-2512",
        "messages": messages,
        "max_tokens": 600,
        "temperature": 0.2,
        "top_p": 0.95,
        "stream": False
    }

    print("trying response...")

    try:
        response = requests.post(
            URL,
            headers=headers,
            json=payload,
            timeout=REQUEST_TIMEOUT
        )

        print("status:", response.status_code)

        response.raise_for_status()
        data = response.json()

        assistant_reply = data["choices"][0]["message"]["content"]

        last_messages.append({"role": "user", "content": message})
        last_messages.append({"role": "assistant", "content": assistant_reply})
 
        if len(last_messages) > context_len:
            last_messages.pop(0)
            last_messages.pop(0)

        return {
            "error": False,
            "response": assistant_reply
        }

    except requests.exceptions.Timeout:
        return {
            "error": True,
            "message": "Timeout: model took too long to respond"
        }

    except requests.exceptions.RequestException as e:
        return {
            "error": True,
            "message": f"HTTP error: {str(e)}"
        }

    except Exception as e:
        return {
            "error": True,
            "message": f"Unexpected error: {str(e)}"
        }
