import os
import requests

LLM_API_BASE = os.getenv('LLM_API_BASE', 'http://localhost:11434')
LLM_MODEL = os.getenv('LLM_MODEL', 'qwen2.5:7b-instruct')
LLM_TIMEOUT = float(os.getenv('LLM_TIMEOUT', '120'))


def chat(prompt, system=None, temperature=0.3):
    if not prompt:
        raise ValueError('prompt is required')

    payload = {
        'model': LLM_MODEL,
        'prompt': prompt if isinstance(prompt, str) else '\n'.join(prompt),
        'stream': False,
        'options': {'temperature': temperature},
    }
    if system:
        payload['system'] = system

    resp = requests.post(f"{LLM_API_BASE}/api/generate", json=payload, timeout=LLM_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    if 'response' not in data:
        raise RuntimeError(f"LLM response missing 'response': {data}")
    return data['response'].strip()
