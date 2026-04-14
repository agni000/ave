import re

# Remove formatações simples e substitui quebras de linha por espaços para normalizar o texto 
def clean_text(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    text = re.sub(r"\n+", " ", text)
    return text.strip()

# Gera um preview curto do texto que é usado na aba de histórico
def make_preview(text: str, limit: int = 60) -> str:
    text = clean_text(text)
    return text[:limit] + "..." if len(text) > limit else text
