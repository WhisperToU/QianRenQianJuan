"""
Shared AI helpers for routes.
Centralizes system prompts and small orchestration helpers
so individual route files stay thin.
"""

import os
from functools import lru_cache
from typing import Optional

from utils.llm_client import chat

_BASE_DIR = os.path.dirname(__file__)
_ROOT_DIR = os.path.dirname(_BASE_DIR)
_PROMPT_DIR = os.path.join(_ROOT_DIR, "prompt")
_PUBLIC_PROMPT_PATH = os.path.join(_PROMPT_DIR, "system_public.txt")
_SECURE_PROMPT_PATH = os.path.join(_PROMPT_DIR, "system_secure.txt")

# Fallback prompts (used if prompt files are missing)
DEFAULT_PUBLIC_SYSTEM_PROMPT = (
    "You are a concise, friendly teaching assistant. "
    "Keep answers short, clear, and safe."
)

SECURE_SYSTEM_PROMPT = (
    "You are a secure-mode teaching assistant for authenticated staff. "
    "Emphasize safety, note that this response is coming from the secure path, "
    "and keep the reply concise and actionable."
)


@lru_cache(maxsize=1)
def get_secure_system_prompt() -> str:
    """Load secure system prompt from file once; fallback to the builtin."""
    try:
        with open(_SECURE_PROMPT_PATH, "r", encoding="utf-8") as f:
            text = f.read().strip()
            return text or SECURE_SYSTEM_PROMPT
    except FileNotFoundError:
        return SECURE_SYSTEM_PROMPT


@lru_cache(maxsize=1)
def get_public_system_prompt() -> str:
    """Load public system prompt from file once; fallback to default."""
    try:
        with open(_PUBLIC_PROMPT_PATH, "r", encoding="utf-8") as f:
            text = f.read().strip()
            return text or DEFAULT_PUBLIC_SYSTEM_PROMPT
    except FileNotFoundError:
        return DEFAULT_PUBLIC_SYSTEM_PROMPT


def generate_response(
    prompt: str,
    *,
    system: Optional[str] = None,
    temperature: float = 0.3,
) -> str:
    """Basic wrapper around the LLM client."""
    return chat(prompt, system=system, temperature=temperature)


def generate_public_response(prompt: str, *, temperature: float = 0.3) -> str:
    """Public-facing chat with a lightweight guardrail prompt."""
    system = get_public_system_prompt()
    return generate_response(prompt, system=system, temperature=temperature)


def generate_secure_response(prompt: str, *, temperature: float = 0.3) -> str:
    """Auth-required chat with a stricter system prompt."""
    system = get_secure_system_prompt()
    return generate_response(prompt, system=system, temperature=temperature)
