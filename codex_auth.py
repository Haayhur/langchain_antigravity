"""
OpenAI Codex OAuth authentication for LangChain.

Based on opencode-openai-codex-auth by Numman Ali:
https://github.com/numman-ali/opencode-openai-codex-auth
"""

import base64
import hashlib
import json
import os
import secrets
import time
import webbrowser
from dataclasses import dataclass, field
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from threading import Thread
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

import httpx

from .constants import (
    CODEX_CLIENT_ID,
    CODEX_AUTHORIZE_URL,
    CODEX_TOKEN_URL,
    CODEX_REDIRECT_URI,
    CODEX_SCOPE,
    CODEX_BASE_URL,
    CODEX_DUMMY_API_KEY,
    CODEX_HEADERS,
    CODEX_MODEL_MAPPINGS,
)


@dataclass
class CodexAuth:
    access_token: str
    refresh_token: str
    expires_at: float
    account_id: str | None = None

    def is_expired(self, buffer_seconds: int = 60) -> bool:
        return time.time() >= (self.expires_at - buffer_seconds)

    def to_dict(self) -> dict[str, Any]:
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at,
            "account_id": self.account_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CodexAuth":
        return cls(
            access_token=data.get("access_token", ""),
            refresh_token=data.get("refresh_token", ""),
            expires_at=data.get("expires_at", 0),
            account_id=data.get("account_id"),
        )


@dataclass
class CodexAccountStorage:
    version: int = 1
    accounts: list[dict[str, Any]] = field(default_factory=list)
    active_index: int = 0

    def get_active_account(self) -> dict[str, Any] | None:
        if 0 <= self.active_index < len(self.accounts):
            return self.accounts[self.active_index]
        return self.accounts[0] if self.accounts else None


def get_codex_config_dir() -> Path:
    """Get the langchain-antigravity codex config directory."""
    if os.name == "nt":
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            return Path(appdata) / "langchain-antigravity" / "codex"
    return Path.home() / ".config" / "langchain-antigravity" / "codex"


def get_codex_accounts_path() -> Path:
    return get_codex_config_dir() / "accounts.json"


def load_codex_accounts() -> CodexAccountStorage | None:
    path = get_codex_accounts_path()

    if not path.exists():
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return CodexAccountStorage(
            version=data.get("version", 1),
            accounts=data.get("accounts", []),
            active_index=data.get("activeIndex", 0),
        )
    except (json.JSONDecodeError, OSError):
        return None


def save_codex_accounts(storage: CodexAccountStorage) -> None:
    path = get_codex_accounts_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "version": storage.version,
        "accounts": storage.accounts,
        "activeIndex": storage.active_index,
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def generate_pkce() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(32)
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return verifier, challenge


def decode_jwt(token: str) -> dict[str, Any] | None:
    """Decode a JWT token to extract payload."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        payload = parts[1]
        decoded = base64.urlsafe_b64decode(payload + "=" * (4 - len(payload) % 4))
        return json.loads(decoded)
    except Exception:
        return None


def extract_account_id(access_token: str) -> str | None:
    """Extract ChatGPT account ID from JWT access token."""
    try:
        payload = decode_jwt(access_token)
        if not payload:
            return None

        claim_path = "https://api.openai.com/auth"
        auth_data = payload.get(claim_path, {})
        return auth_data.get("chatgpt_account_id")
    except Exception:
        return None


def authorize_codex() -> tuple[str, str, str]:
    """Generate authorization URL and state for Codex OAuth flow."""
    verifier, challenge = generate_pkce()
    state = secrets.token_hex(16)

    params = {
        "response_type": "code",
        "client_id": CODEX_CLIENT_ID,
        "redirect_uri": CODEX_REDIRECT_URI,
        "scope": CODEX_SCOPE,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "state": state,
        "id_token_add_organizations": "true",
        "codex_cli_simplified_flow": "true",
        "originator": "codex_cli_rs",
    }

    url = f"{CODEX_AUTHORIZE_URL}?{urlencode(params)}"
    return url, verifier, state


async def exchange_codex_token(code: str, verifier: str) -> CodexAuth:
    start_time = time.time()

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            CODEX_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "client_id": CODEX_CLIENT_ID,
                "code": code,
                "code_verifier": verifier,
                "redirect_uri": CODEX_REDIRECT_URI,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if not response.is_success:
            raise ValueError(f"Token exchange failed: {response.text}")

        token_data = response.json()
        access_token = token_data.get("access_token", "")
        refresh_token = token_data.get("refresh_token", "")
        expires_in = token_data.get("expires_in", 3600)

        if not access_token or not refresh_token:
            raise ValueError("Missing required tokens in response")

        account_id = extract_account_id(access_token)

        return CodexAuth(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=start_time + expires_in,
            account_id=account_id,
        )


async def refresh_codex_token(auth: CodexAuth) -> CodexAuth:
    if not auth.refresh_token:
        raise ValueError("Missing refresh token")

    start_time = time.time()

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            CODEX_TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": auth.refresh_token,
                "client_id": CODEX_CLIENT_ID,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if not response.is_success:
            data = response.json() if response.headers.get("content-type", "").startswith(
                "application/json"
            ) else {}
            error_code = data.get("error", "")
            if error_code == "invalid_grant":
                raise ValueError("Refresh token revoked - run 'codex-auth login' again")
            raise ValueError(f"Token refresh failed: {response.text}")

        token_data = response.json()

        return CodexAuth(
            access_token=token_data.get("access_token", ""),
            refresh_token=token_data.get("refresh_token", auth.refresh_token),
            expires_at=start_time + token_data.get("expires_in", 3600),
            account_id=auth.account_id,
        )


class CodexOAuthCallbackHandler(BaseHTTPRequestHandler):
    code: str | None = None
    state: str | None = None

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/auth/callback":
            params = parse_qs(parsed.query)
            CodexOAuthCallbackHandler.code = params.get("code", [None])[0]
            CodexOAuthCallbackHandler.state = params.get("state", [None])[0]

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"""
                <html><body style="font-family: system-ui; text-align: center; padding: 50px;">
                <h1>Authentication Successful!</h1>
                <p>You can close this window and return to your terminal.</p>
                <script>window.close();</script>
                </body></html>
            """)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format: str, *args: Any) -> None:
        pass


async def codex_interactive_login() -> CodexAuth:
    CodexOAuthCallbackHandler.code = None
    CodexOAuthCallbackHandler.state = None

    auth_url, verifier, state = authorize_codex()

    server = HTTPServer(("localhost", 1455), CodexOAuthCallbackHandler)
    server_thread = Thread(target=server.handle_request, daemon=True)
    server_thread.start()

    print("\nOpening browser for ChatGPT authentication...")
    print(f"If browser doesn't open, visit:\n{auth_url}\n")
    webbrowser.open(auth_url)

    server_thread.join(timeout=120)
    server.server_close()

    if not CodexOAuthCallbackHandler.code:
        raise ValueError("OAuth callback not received - authentication timed out")

    auth = await exchange_codex_token(CodexOAuthCallbackHandler.code, verifier)

    storage = load_codex_accounts() or CodexAccountStorage()

    existing_idx = next(
        (i for i, acc in enumerate(storage.accounts)
         if acc.get("account_id") == auth.account_id),
        None
    )

    if existing_idx is not None:
        storage.accounts[existing_idx] = {
            "account_id": auth.account_id,
            "refresh_token": auth.refresh_token,
            "addedAt": storage.accounts[existing_idx].get("addedAt", int(time.time() * 1000)),
            "lastUsed": int(time.time() * 1000),
        }
        storage.active_index = existing_idx
    else:
        storage.accounts.append({
            "account_id": auth.account_id,
            "refresh_token": auth.refresh_token,
            "addedAt": int(time.time() * 1000),
            "lastUsed": int(time.time() * 1000),
        })
        storage.active_index = len(storage.accounts) - 1

    save_codex_accounts(storage)

    print(f"Authenticated (account ID: {auth.account_id})")
    print(f"Credentials saved to {get_codex_accounts_path()}")
    return auth


def load_codex_auth_from_storage() -> CodexAuth | None:
    storage = load_codex_accounts()
    if not storage or not storage.accounts:
        return None

    account = storage.get_active_account()
    if not account:
        return None

    return CodexAuth(
        access_token="",
        refresh_token=account.get("refresh_token", ""),
        expires_at=0,
        account_id=account.get("account_id"),
    )


def list_codex_accounts() -> list[dict[str, Any]]:
    storage = load_codex_accounts()
    if not storage:
        return []
    return [
        {"account_id": acc.get("account_id", "Unknown"), "active": i == storage.active_index}
        for i, acc in enumerate(storage.accounts)
    ]


def set_active_codex_account(account_id: str) -> bool:
    storage = load_codex_accounts()
    if not storage:
        return False

    for i, acc in enumerate(storage.accounts):
        if acc.get("account_id") == account_id:
            storage.active_index = i
            save_codex_accounts(storage)
            return True
    return False


def remove_codex_account(account_id: str) -> bool:
    storage = load_codex_accounts()
    if not storage:
        return False

    for i, acc in enumerate(storage.accounts):
        if acc.get("account_id") == account_id:
            storage.accounts.pop(i)
            if storage.active_index >= len(storage.accounts):
                storage.active_index = max(0, len(storage.accounts) - 1)
            save_codex_accounts(storage)
            return True
    return False


def normalize_codex_model(model: str) -> str:
    """Normalize model name to Codex backend format."""
    return CODEX_MODEL_MAPPINGS.get(model, model)
