"""
LLM client with primary → secondary failover.

Assumes both endpoints expose an OpenAI-compatible /v1/chat/completions API
(e.g. Ollama with --api openai, LM Studio, vLLM, llama.cpp server, etc.).

Failover flow:
  1. Try primary_endpoint.
  2. If it raises any exception (timeout, connection error, 5xx), log it and
     immediately retry against secondary_endpoint.
  3. If secondary also fails, raise the error to the route handler.

All I/O is async so a slow model request never blocks other concurrent requests.
"""

import time
import logging
import httpx
from config.settings import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


def _build_payload(system_prompt: str, user_message: str, history: list[dict]) -> dict:
    """
    Build the OpenAI-compatible request body.

    history is a list of prior {role, content} turns (user + assistant alternating).
    The current user_message is appended after history so the model has full context.
    """
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})
    return {
        "model": settings.model_name,
        "messages": messages,
    }


async def _post_to_endpoint(base_url: str, payload: dict) -> dict:
    """
    POST to a single endpoint and return the parsed JSON response.
    Raises httpx.HTTPError or httpx.TimeoutException on failure.
    """
    url = f"{base_url.rstrip('/')}/v1/chat/completions"
    async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()


async def chat_with_failover(
    system_prompt: str,
    user_message: str,
    mode: str,
    history: list[dict] | None = None,
) -> dict:
    """
    Send a chat request, failing over to the secondary server if needed.

    Returns a dict with:
      - reply (str): the assistant's text
      - server_used (str): which endpoint responded
      - latency_ms (int): round-trip time in milliseconds
    """
    payload = _build_payload(system_prompt, user_message, history or [])

    endpoints = [
        ("primary", settings.primary_endpoint),
        ("secondary", settings.secondary_endpoint),
    ]

    last_error: Exception | None = None

    for label, base_url in endpoints:
        start = time.monotonic()
        try:
            logger.info("Attempting %s endpoint (%s) | mode=%s", label, base_url, mode)
            data = await _post_to_endpoint(base_url, payload)
            latency_ms = int((time.monotonic() - start) * 1000)

            reply = data["choices"][0]["message"]["content"]

            logger.info(
                "Success | server=%s | mode=%s | latency=%dms",
                label,
                mode,
                latency_ms,
            )
            return {
                "reply": reply,
                "server_used": label,
                "latency_ms": latency_ms,
            }

        except Exception as exc:
            latency_ms = int((time.monotonic() - start) * 1000)
            logger.warning(
                "Failed %s endpoint | mode=%s | latency=%dms | error=%s",
                label,
                mode,
                latency_ms,
                exc,
            )
            last_error = exc

    # Both servers failed
    raise RuntimeError(f"All LLM endpoints failed. Last error: {last_error}") from last_error


async def health_check() -> dict:
    """
    Check both endpoints by hitting /v1/models — a real API path, not just the
    landing page. Non-2xx responses (including 404 pages) are reported as unhealthy.
    """
    results = {}
    for label, base_url in [
        ("primary", settings.primary_endpoint),
        ("secondary", settings.secondary_endpoint),
    ]:
        url = f"{base_url.rstrip('/')}/v1/models"
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(url)
                if resp.status_code < 300:
                    results[label] = {"status": "ok", "code": resp.status_code}
                else:
                    results[label] = {"status": "unhealthy", "code": resp.status_code}
        except Exception as exc:
            results[label] = {"status": "unreachable", "error": str(exc)}

    return results
