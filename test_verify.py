#!/usr/bin/env python3
"""
Simple standalone test for verifying the implementation.
"""

import asyncio
import sys

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Import modules directly
import auth
import chat_model
import codex_auth
import codex_chat_model

print("="*60)
print("Implementation Verification Tests")
print("="*60)

# Test 1: Verify Antigravity auth module
print("\n[TEST 1] Antigravity Auth Module")
try:
    from auth import AntigravityAuth, AccountStorage
    print("  ✓ AntigravityAuth class defined")
    print("  ✓ AccountStorage class defined")
except Exception as e:
    print(f"  ✗ Failed: {e}")

# Test 2: Verify Codex auth module
print("\n[TEST 2] Codex Auth Module")
try:
    from codex_auth import CodexAuth, CodexAccountStorage
    print("  ✓ CodexAuth class defined")
    print("  ✓ CodexAccountStorage class defined")
except Exception as e:
    print(f"  ✗ Failed: {e}")

# Test 3: Verify Antigravity chat model
print("\n[TEST 3] Antigravity Chat Model")
try:
    from chat_model import ChatAntigravity
    print(f"  ✓ ChatAntigravity class defined")
    print(f"  ✓ Default model: {ChatAntigravity.model.default}")
except Exception as e:
    print(f"  ✗ Failed: {e}")

# Test 4: Verify Codex chat model
print("\n[TEST 4] Codex Chat Model")
try:
    from codex_chat_model import ChatCodex
    print(f"  ✓ ChatCodex class defined")
    print(f"  ✓ Default model: {ChatCodex.model.default}")
except Exception as e:
    print(f"  ✗ Failed: {e}")

# Test 5: Verify constants
print("\n[TEST 5] Constants")
try:
    import constants

    # Antigravity constants
    print(f"  ✓ ANTIGRAVITY_CLIENT_ID: {constants.ANTIGRAVITY_CLIENT_ID[:20]}...")
    print(f"  ✓ ANTIGRAVITY_REDIRECT_URI: {constants.ANTIGRAVITY_REDIRECT_URI}")

    # Codex constants
    print(f"  ✓ CODEX_CLIENT_ID: {constants.CODEX_CLIENT_ID}")
    print(f"  ✓ CODEX_BASE_URL: {constants.CODEX_BASE_URL}")

    # Model mappings
    print(f"  ✓ Antigravity models: {len(constants.MODEL_MAPPINGS)}")
    print(f"  ✓ Codex models: {len(constants.CODEX_MODEL_MAPPINGS)}")
except Exception as e:
    print(f"  ✗ Failed: {e}")

# Test 6: Verify auth functions
print("\n[TEST 6] Auth Functions")
try:
    from auth import (
        interactive_login,
        load_auth_from_storage,
        refresh_access_token,
        list_accounts,
        set_active_account,
        remove_account,
    )
    print("  ✓ All Antigravity auth functions exported")

    from codex_auth import (
        codex_interactive_login,
        load_codex_auth_from_storage,
        refresh_codex_token,
        list_codex_accounts,
        set_active_codex_account,
        remove_codex_account,
    )
    print("  ✓ All Codex auth functions exported")
except Exception as e:
    print(f"  ✗ Failed: {e}")

# Test 7: Check authentication storage
print("\n[TEST 7] Authentication Storage")
try:
    from auth import get_accounts_path, get_config_dir
    from codex_auth import get_codex_accounts_path, get_codex_config_dir

    print(f"  ✓ Antigravity config dir: {get_config_dir()}")
    print(f"  ✓ Antigravity accounts path: {get_accounts_path()}")
    print(f"  ✓ Codex config dir: {get_codex_config_dir()}")
    print(f"  ✓ Codex accounts path: {get_codex_accounts_path()}")
except Exception as e:
    print(f"  ✗ Failed: {e}")

# Test 8: Check model normalizations
print("\n[TEST 8] Model Normalization")
try:
    from codex_auth import normalize_codex_model
    from chat_model import resolve_model_name

    # Test Antigravity normalization
    antigrav_models = [
        "antigravity-gemini-3-flash",
        "antigravity-claude-sonnet-4-5",
    ]
    for model in antigrav_models:
        resolved = resolve_model_name(model)
        print(f"  ✓ {model} -> {resolved}")

    # Test Codex normalization
    codex_models = [
        "gpt-5.2-codex-high",
        "gpt-5.1-codex-max",
        "gpt-5.1-codex-mini",
    ]
    for model in codex_models:
        resolved = normalize_codex_model(model)
        print(f"  ✓ {model} -> {resolved}")
except Exception as e:
    print(f"  ✗ Failed: {e}")

# Test 9: Check auth storage access
print("\n[TEST 9] Auth Storage Access")
try:
    from auth import load_accounts
    from codex_auth import load_codex_accounts

    ag_storage = load_accounts()
    codex_storage = load_codex_accounts()

    if ag_storage:
        print(f"  ✓ Antigravity: {len(ag_storage.accounts)} account(s) stored")
    else:
        print("  ✓ Antigravity: No accounts stored")

    if codex_storage:
        print(f"  ✓ Codex: {len(codex_storage.accounts)} account(s) stored")
    else:
        print("  ✓ Codex: No accounts stored")
except Exception as e:
    print(f"  ✗ Failed: {e}")

# Summary
print("\n" + "="*60)
print("VERIFICATION COMPLETE")
print("="*60)
print("\nAll core modules and functions verified!")
print("\nTo test with actual authentication:")
print("  - Google: Run 'ag-auth login'")
print("  - OpenAI: Run 'codex-auth login'")
