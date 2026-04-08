import requests
from core.config import NVIDIA_API_KEY

URL = "https://integrate.api.nvidia.com/v1/chat/completions"
REQUEST_TIMEOUT = 30

def generate_response(message: str):
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Accept": "application/json"
    }

    payload = {
        "model": "mistralai/ministral-14b-instruct-2512",
        "messages": [
            {
                "role": "system",
                "content": """You are a guitar assistant.

                - Always respond in Portuguese
                - Be concise and direct
                - Use short answers (max 3 lines)
                - Do NOT explain unless asked
                - Do NOT add extra context
                - Prefer bullet points or simple chord lines
                - If possible, answer in a single line

                Examples:
                User: Me dê uma progressão triste
                Assistant: Am - F - C - G

                User: Como fazer acorde de G?
                Assistant: 3º traste (E), 2º traste (A), 3º traste (e)
                """
            },
            {
                "role": "user",
                "content": message
            }
        ],
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

        return {
            "error": False,
            "response": data["choices"][0]["message"]["content"]
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
