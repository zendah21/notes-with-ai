import os
import json
import re
import time
import threading
from typing import Dict, List, Tuple, Any
from huggingface_hub import InferenceClient


_client_lock = threading.Lock()
_client = None


def _get_client() -> InferenceClient:
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:
                _client = InferenceClient(token=os.getenv("HF_API_TOKEN"))
    return _client


_cache: Dict[str, Tuple[float, Any]] = {}


def _cache_get(key: str, ttl=60):
    t = _cache.get(key)
    if not t:
        return None
    ts, val = t
    if time.time() - ts < ttl:
        return val
    return None


def _cache_set(key: str, val: Any):
    _cache[key] = (time.time(), val)


def _retry(fn, *, attempts=3, backoff=0.8):
    last = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as e:
            last = e
            time.sleep(backoff * (2**i))
    raise last


def hf_zero_shot(text: str, labels: List[str]) -> Tuple[str, Dict[str, float]]:
    key = f"zs::{hash(text)}::{','.join(labels)}::{os.getenv('HF_CLASSIFIER_MODEL_ZEROSHOT','facebook/bart-large-mnli')}"
    cached = _cache_get(key)
    if cached is not None:
        return cached

    def _call():
        client = _get_client()
        model = os.getenv("HF_CLASSIFIER_MODEL_ZEROSHOT", "facebook/bart-large-mnli")
        res = client.zero_shot_classification(text, labels=labels, model=model, timeout=6.0)
        # Expected res: {labels:[], scores:[]}
        best = None
        scores = {}
        for l, s in zip(res.get("labels", []), res.get("scores", [])):
            scores[l] = float(s)
            if best is None or s > scores[best]:
                best = l
        return best or labels[0], scores

    val = _retry(_call)
    _cache_set(key, val)
    return val


def hf_ner(text: str):
    key = f"ner::{hash(text)}::{os.getenv('HF_NER_MODEL','dslim/bert-base-NER')}"
    cached = _cache_get(key)
    if cached is not None:
        return cached

    def _call():
        client = _get_client()
        model = os.getenv("HF_NER_MODEL", "dslim/bert-base-NER")
        return client.token_classification(text, model=model, timeout=6.0)

    val = _retry(_call)
    _cache_set(key, val)
    return val


def _strip_to_json(text: str) -> dict:
    # strip code fences & find first { ... }
    if not text:
        return {}
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        return {}
    s = m.group(0)
    # simple repair: remove trailing commas
    s = re.sub(r",(\s*[}\]])", r"\1", s)
    try:
        return json.loads(s)
    except Exception:
        return {}


def hf_text2json(prompt: str) -> dict:
    key = f"t2j::{hash(prompt)}::{os.getenv('HF_TASK_MODEL_TEXT2TEXT','google/flan-t5-base')}"
    cached = _cache_get(key)
    if cached is not None:
        return cached

    def _call():
        client = _get_client()
        model = os.getenv("HF_TASK_MODEL_TEXT2TEXT", "google/flan-t5-base")
        raw = client.text_generation(
            prompt=prompt,
            model=model,
            max_new_tokens=256,
            temperature=0.2,
            timeout=10.0,
        )
        if isinstance(raw, dict) and "generated_text" in raw:
            txt = raw["generated_text"]
        elif isinstance(raw, list) and raw and isinstance(raw[0], dict) and "generated_text" in raw[0]:
            txt = raw[0]["generated_text"]
        else:
            txt = str(raw)
        return _strip_to_json(txt)

    val = _retry(_call)
    _cache_set(key, val)
    return val

