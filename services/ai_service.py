# services/ai_service.py

from utils.llm_client import chat


def load_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def get_secure_system_prompt():
    return load_file("prompt/system_secure.txt")


def get_public_system_prompt():
    return load_file("prompt/system_public.txt")


def generate_secure_response(prompt: str, temperature: float = 0.3) -> str:
    system = get_secure_system_prompt()
    return chat(prompt, system=system, temperature=temperature)


def generate_public_response(prompt: str, temperature: float = 0.3) -> str:
    system = get_public_system_prompt()
    return chat(prompt, system=system, temperature=temperature)
