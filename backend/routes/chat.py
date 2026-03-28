"""
POST /chat  — main chat endpoint
GET  /health — server reachability check
"""

import json
import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from services import chat_with_failover, health_check, get_mode_config
from services.mode_config import MODE_CONFIGS

logger = logging.getLogger(__name__)

router = APIRouter()

# Single source of truth — valid modes are whatever MODE_CONFIGS defines
VALID_MODES = set(MODE_CONFIGS.keys())

# Upload limits
MAX_FILE_BYTES = 512 * 1024   # 512 KB per file; silently skip larger ones
MAX_TOTAL_CHARS = 8_000       # total chars injected into prompt across all files


class ChatResponse(BaseModel):
    reply: str
    mode: str
    server_used: str
    latency_ms: int


@router.post("/chat", response_model=ChatResponse)
async def chat(
    message: str = Form(...),
    mode: str = Form(default="general"),
    # JSON-encoded list of prior {role, content} turns, oldest first.
    # Empty array means no prior context (first message in a session).
    history: str = Form(default="[]"),
    files: list[UploadFile] = File(default=[]),
):
    """
    Accept a user message, conversation history, and optional uploaded files.
    Mode determines which system prompt is used.

    history format: JSON string — [{"role":"user","content":"..."},
                                    {"role":"assistant","content":"..."},...]
    Files: text extraction only; hard limits on per-file size and total chars injected.
    """
    if mode not in VALID_MODES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode '{mode}'. Must be one of {sorted(VALID_MODES)}.",
        )

    # RAG mode stub — retrieval not yet implemented
    if mode == "rag":
        logger.info("RAG mode requested but not yet implemented — falling back to general prompt")

    # --- Parse conversation history ---
    try:
        parsed_history: list[dict] = json.loads(history)
        if not isinstance(parsed_history, list):
            raise ValueError("history must be a JSON array")
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid history field: {exc}")

    # --- File handling ---
    file_text_parts: list[str] = []
    total_chars = 0

    for upload in files:
        raw = await upload.read()

        if len(raw) > MAX_FILE_BYTES:
            logger.warning("Skipping oversized file %s (%d bytes)", upload.filename, len(raw))
            continue

        if total_chars >= MAX_TOTAL_CHARS:
            logger.warning("Prompt char budget exhausted; skipping %s", upload.filename)
            break

        try:
            text = raw.decode("utf-8", errors="ignore").strip()
            if not text:
                logger.warning("Skipping non-text or empty file: %s", upload.filename)
                continue
            chunk = text[: MAX_TOTAL_CHARS - total_chars]
            file_text_parts.append(f"[Attachment: {upload.filename}]\n{chunk}")
            total_chars += len(chunk)
        except Exception as exc:
            logger.warning("Could not read file %s: %s", upload.filename, exc)

    full_message = message
    if file_text_parts:
        full_message = message + "\n\n" + "\n\n".join(file_text_parts)

    logger.info(
        "Chat request | mode=%s | history_turns=%d | files=%d | message_len=%d",
        mode, len(parsed_history), len(files), len(full_message),
    )

    config = get_mode_config(mode)

    try:
        result = await chat_with_failover(
            system_prompt=config.system_prompt,
            user_message=full_message,
            mode=mode,
            history=parsed_history,
        )
    except RuntimeError as exc:
        logger.error("All LLM endpoints failed: %s", exc)
        raise HTTPException(status_code=503, detail="LLM service unavailable. Please try again later.")

    return ChatResponse(
        reply=result["reply"],
        mode=mode,
        server_used=result["server_used"],
        latency_ms=result["latency_ms"],
    )


@router.get("/health")
async def health():
    """Check reachability and API usability of both LLM endpoints."""
    return await health_check()
