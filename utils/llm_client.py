import logging
import os
from typing import Sequence, Union

import requests

LLM_API_BASE = os.getenv('LLM_API_BASE', 'http://localhost:11434')
LLM_MODEL = os.getenv('LLM_MODEL', 'qwen2.5:7b-instruct')
LLM_TIMEOUT = float(os.getenv('LLM_TIMEOUT', '120'))
LOGGER = logging.getLogger(__name__)


def _ensure_prompt(prompt: Union[str, Sequence[str]]) -> str:
    return prompt if isinstance(prompt, str) else '\n'.join(prompt)


def chat(prompt: Union[str, Sequence[str]], system: str | None = None, temperature: float = 0.3) -> str:
    final_prompt = _ensure_prompt(prompt)
    if not final_prompt:
        raise ValueError('prompt is required')

    payload = {
        'model': LLM_MODEL,
        'prompt': final_prompt,
        'stream': False,
        'options': {'temperature': temperature},
    }
    if system:
        payload['system'] = system

    try:
        resp = requests.post(f"{LLM_API_BASE}/api/generate", json=payload, timeout=LLM_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as exc:
        LOGGER.warning('LLM request failed (%s): %s', LLM_API_BASE, exc)
        raise RuntimeError(f"LLM 服务不可达：{exc}") from exc

    data = resp.json()
    if 'response' not in data:
        raise RuntimeError(f"LLM response missing 'response': {data}")
    return data['response'].strip()
