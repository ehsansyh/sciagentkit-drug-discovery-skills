from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class HttpConfig:
    timeout: float = 30.0
    retries: int = 2
    backoff_seconds: float = 0.75
    user_agent: str = "SciAgentKit/1.0 (+https://github.com/ehsansyh/sciagentkit-drug-discovery-skills)"


class SciAgentHttpError(RuntimeError):
    """Raised when a remote scientific resource cannot be retrieved."""


def request_json(
    url: str,
    *,
    params: dict[str, Any] | None = None,
    method: str = "GET",
    json_body: dict[str, Any] | None = None,
    config: HttpConfig | None = None,
) -> Any:
    cfg = config or HttpConfig()
    headers = {"User-Agent": cfg.user_agent, "Accept": "application/json"}
    last_error: Exception | None = None
    for attempt in range(cfg.retries + 1):
        try:
            if method.upper() == "POST":
                response = requests.post(url, params=params, json=json_body, timeout=cfg.timeout, headers=headers)
            else:
                response = requests.get(url, params=params, timeout=cfg.timeout, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as exc:  # pragma: no cover - network dependent
            last_error = exc
            if attempt < cfg.retries:
                time.sleep(cfg.backoff_seconds * (attempt + 1))
    raise SciAgentHttpError(f"Failed to fetch JSON from {url}: {last_error}")


def request_text(url: str, *, params: dict[str, Any] | None = None, config: HttpConfig | None = None) -> str:
    cfg = config or HttpConfig()
    headers = {"User-Agent": cfg.user_agent, "Accept": "text/plain,*/*"}
    last_error: Exception | None = None
    for attempt in range(cfg.retries + 1):
        try:
            response = requests.get(url, params=params, timeout=cfg.timeout, headers=headers)
            response.raise_for_status()
            return response.text
        except Exception as exc:  # pragma: no cover - network dependent
            last_error = exc
            if attempt < cfg.retries:
                time.sleep(cfg.backoff_seconds * (attempt + 1))
    raise SciAgentHttpError(f"Failed to fetch text from {url}: {last_error}")
