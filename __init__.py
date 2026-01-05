"""
LangChain Antigravity - Access Gemini 3 and Claude models via Google OAuth.

Based on opencode-antigravity-auth by NoeFabris:
https://github.com/NoeFabris/opencode-antigravity-auth
"""

from .chat_model import ChatAntigravity
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

__all__ = [
    "ChatAntigravity",
    "AntigravityAuth",
    "authorize_antigravity",
    "exchange_token",
    "refresh_access_token",
    "load_accounts",
    "save_accounts",
    "interactive_login",
    "load_auth_from_storage",
    "list_accounts",
    "set_active_account",
    "remove_account",
]

__version__ = "0.1.0"
