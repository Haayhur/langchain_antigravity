"""
LangChain Antigravity - Access Gemini 3, Claude models via Google OAuth,
and GPT-5.x/Codex models via OpenAI OAuth.

Based on:
- opencode-antigravity-auth by NoeFabris: https://github.com/NoeFabris/opencode-antigravity-auth
- opencode-openai-codex-auth by Numman Ali: https://github.com/numman-ali/opencode-openai-codex-auth
"""

from .chat_model import ChatAntigravity
from .codex_chat_model import ChatCodex
from .auth import (
    AntigravityAuth,
    authorize_antigravity,
    exchange_token,
    refresh_access_token,
    load_accounts,
    save_accounts,
    interactive_login,
    load_auth_from_storage,
    list_accounts,
    set_active_account,
    remove_account,
)
from .codex_auth import (
    CodexAuth,
    authorize_codex,
    exchange_codex_token,
    refresh_codex_token,
    load_codex_accounts,
    save_codex_accounts,
    codex_interactive_login,
    load_codex_auth_from_storage,
    list_codex_accounts,
    set_active_codex_account,
    remove_codex_account,
    normalize_codex_model,
)

__all__ = [
    "ChatAntigravity",
    "ChatCodex",
    "AntigravityAuth",
    "CodexAuth",
    "authorize_antigravity",
    "authorize_codex",
    "exchange_token",
    "exchange_codex_token",
    "refresh_access_token",
    "refresh_codex_token",
    "load_accounts",
    "load_codex_accounts",
    "save_accounts",
    "save_codex_accounts",
    "interactive_login",
    "codex_interactive_login",
    "load_auth_from_storage",
    "load_codex_auth_from_storage",
    "list_accounts",
    "list_codex_accounts",
    "set_active_account",
    "set_active_codex_account",
    "remove_account",
    "remove_codex_account",
    "normalize_codex_model",
]

__version__ = "0.2.0"
