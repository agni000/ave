import requests
from core.config import NVIDIA_API_KEY

URL = "https://integrate.api.nvidia.com/v1/chat/completions"

def generate_response(message: str) -> str:
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Accept": "application/json"
    }

    payload = {
        "model": "qwen/qwen3.5-122b-a10b",
        "messages": [
            {
                "role": "system",
                "content": "Você é um especialista em biologia. Responda apenas perguntas relacionadas à biologia. Caso a pergunta não seja sobre biologia, diga educadamente que só pode responder sobre esse tema."
            },
            {
                "role": "user", 
                "content": message
            }, 
        ],
        "temperature": 0.6,
        "top_p": 0.95,
        "max_tokens": 500
    }

    response = requests.post(URL, headers=headers, json=payload)
    data = response.json()

    return data["choices"][0]["message"]["content"]
