"""
Mode configuration: defines system prompts and behavior per chat mode.

Adding a new mode:
  1. Add an entry to MODE_CONFIGS below.
  2. The frontend just needs to send the matching mode string.

Modes:
  - general: General-purpose assistant for internal questions
  - email:   Helps draft or respond to professional emails
  - rag:     (Reserved) Future RAG / document-search mode
"""

from dataclasses import dataclass


@dataclass
class ModeConfig:
    system_prompt: str
    # Placeholder for future per-mode options (temperature, max_tokens, etc.)
    # temperature: float = 0.7


MODE_CONFIGS: dict[str, ModeConfig] = {
    "general": ModeConfig(
        system_prompt=(
            "You are a helpful internal assistant for American Power Systems. "
            "Answer questions clearly and professionally. "
            "If you don't know something, say so rather than guessing."
        ),
    ),
    "email": ModeConfig(
        system_prompt=(
            "You are an expert business communication assistant for American Power Systems. "
            "Help the user draft, refine, or respond to professional emails. "
            "Keep tone professional, concise, and clear. "
            "When given a received email, suggest a polished reply. "
            "When given a request, draft an appropriate email from scratch."
        ),
    ),
    # RAG mode is reserved for future document-retrieval integration.
    # The backend accepts it now but returns a not-implemented response.
    "rag": ModeConfig(
        system_prompt=(
            "You are a document-aware assistant. "
            "(RAG retrieval not yet implemented — responding without document context.)"
        ),
    ),
}

DEFAULT_MODE = "general"


def get_mode_config(mode: str) -> ModeConfig:
    """Return config for the requested mode, falling back to default."""
    return MODE_CONFIGS.get(mode, MODE_CONFIGS[DEFAULT_MODE])
