"""
POST /chat  — main chat endpoint
GET  /health — server reachability check
"""

import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional

from services import chat_with_failover, health_check, get_mode_config

logger = logging.getLogger(__name__)

router = APIRouter()

VALID_MODES = {"general", "email", "rag"}


class ChatResponse(BaseModel):
    reply: str
    mode: str
    server_used: str
    latency_ms: int


@router.post("/chat", response_model=ChatResponse)
async def chat(
    message: str = Form(...),
    mode: str = Form(default="general"),
    files: list[UploadFile] = File(default=[]),
):
    """
    Accept a user message plus optional uploaded files.
    Mode determines which system prompt is used.

    Files: basic text extraction — content is appended to the user message.
    Binary/non-text files are skipped with a warning.
    """
    if mode not in VALID_MODES:
        raise HTTPException(status_code=400, detail=f"Invalid mode '{mode}'. Must be one of {VALID_MODES}.")

    # RAG mode stub — structure exists, retrieval not yet implemented
    if mode == "rag":
        logger.info("RAG mode requested but not yet implemented — falling back to general prompt")

    # --- File handling ---
    file_text_parts: list[str] = []
    for upload in files:
        try:
            raw = await upload.read()
            text = raw.decode("utf-8", errors="ignore").strip()
            if text:
                file_text_parts.append(f"[Attachment: {upload.filename}]\n{text}")
            else:
                logger.warning("Skipping non-text or empty file: %s", upload.filename)
        except Exception as exc:
            logger.warning("Could not read file %s: %s", upload.filename, exc)

    # Combine message and any extracted file text
    full_message = message
    if file_text_parts:
        full_message = message + "\n\n" + "\n\n".join(file_text_parts)

    logger.info("Chat request | mode=%s | files=%d | message_len=%d", mode, len(files), len(full_message))

    # --- Get mode-specific system prompt ---
    config = get_mode_config(mode)

    # --- Call LLM with failover ---
    try:
        result = chat_with_failover(
            system_prompt=config.system_prompt,
            user_message=full_message,
            mode=mode,
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
    """Check reachability of both LLM endpoints."""
    return await health_check()
