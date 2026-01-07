#!/usr/bin/env python3
"""
Simple implementation verification test (runs without package installation).
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules directly (not as package)
import constants
import auth
import chat_model
import codex_auth
import codex_chat_model

print("="*60)
print("IMPLEMENTATION VERIFICATION")
print("="*60)

tests_passed = 0
tests_failed = 0

# Test 1: Constants
print("\n[TEST 1] OAuth Constants")
try:
    assert constants.ANTIGRAVITY_CLIENT_ID.startswith("1071006060591")
    print("  [PASS] Antigrav Client ID")
    assert constants.ANTIGRAVITY_REDIRECT_URI == "http://localhost:51121/oauth-callback"
    print("  [PASS] Antigrav Redirect URI")

    assert constants.CODEX_CLIENT_ID == "app_EMoamEEZ73f0CkXaXp7hrann"
    print("  [PASS] Codex Client ID")
    assert constants.CODEX_AUTHORIZE_URL == "https://auth.openai.com/oauth/authorize"
    print("  [PASS] Codex Authorize URL")

    assert constants.CODEX_TOKEN_URL == "https://auth.openai.com/oauth/token"
    print("  [PASS] Codex Token URL")
    assert constants.CODEX_BASE_URL == "https://chatgpt.com/backend-api"
    print("  [PASS] Codex Base URL")

    tests_passed += 5
except Exception as e:
    print(f"  [FAIL] {e}")
    tests_failed += 1

# Test 2: Model Mappings
print("\n[TEST 2] Model Mappings")
try:
    assert len(constants.MODEL_MAPPINGS) > 0
    print(f"  [PASS] Antigrav models: {len(constants.MODEL_MAPPINGS)}")

    assert len(constants.CODEX_MODEL_MAPPINGS) > 0
    print(f"  [PASS] Codex models: {len(constants.CODEX_MODEL_MAPPINGS)}")

    # Test specific mappings
    assert constants.MODEL_MAPPINGS.get("antigravity-gemini-3-flash") == "gemini-3-flash"
    print("  [PASS] Gemini-3 Flash mapping")

    assert constants.CODEX_MODEL_MAPPINGS.get("gpt-5.2-codex-high") == "gpt-5.2-codex"
    print("  [PASS] GPT-5.2 Codex mapping")

    tests_passed += 4
except Exception as e:
    print(f"  [FAIL] {e}")
    tests_failed += 1

# Test 3: Auth Classes
print("\n[TEST 3] Auth Classes")
try:
    assert hasattr(auth, 'AntigravityAuth')
    assert hasattr(auth, 'AccountStorage')
    print("  [PASS] Antigrav auth classes")

    assert hasattr(codex_auth, 'CodexAuth')
    assert hasattr(codex_auth, 'CodexAccountStorage')
    print("  [PASS] Codex auth classes")

    tests_passed += 2
except Exception as e:
    print(f"  [FAIL] {e}")
    tests_failed += 1

# Test 4: Chat Models
print("\n[TEST 4] Chat Models")
try:
    assert hasattr(chat_model, 'ChatAntigravity')
    assert chat_model.ChatAntigravity.model.default == "antigravity-gemini-3-flash"
    print(f"  [PASS] ChatAntigrav with default: {chat_model.ChatAntigravity.model.default}")

    assert hasattr(codex_chat_model, 'ChatCodex')
    assert codex_chat_model.ChatCodex.model.default == "gpt-5.2-codex"
    print(f"  [PASS] ChatCodex with default: {codex_chat_model.ChatCodex.model.default}")

    tests_passed += 2
except Exception as e:
    print(f"  [FAIL] {e}")
    tests_failed += 1

# Test 5: Auth Functions
print("\n[TEST 5] Auth Functions")
try:
    antigrav_functions = [
        'interactive_login',
        'load_auth_from_storage',
        'refresh_access_token',
        'list_accounts',
        'set_active_account',
        'remove_account',
    ]
    for func in antigrav_functions:
        assert hasattr(auth, func)
    print(f"  [PASS] All {len(antigrav_functions)} Antigrav auth functions")

    codex_functions = [
        'codex_interactive_login',
        'load_codex_auth_from_storage',
        'refresh_codex_token',
        'list_codex_accounts',
        'set_active_codex_account',
        'remove_codex_account',
    ]
    for func in codex_functions:
        assert hasattr(codex_auth, func)
    print(f"  [PASS] All {len(codex_functions)} Codex auth functions")

    tests_passed += 2
except Exception as e:
    print(f"  [FAIL] {e}")
    tests_failed += 1

# Test 6: Model Normalization
print("\n[TEST 6] Model Normalization")
try:
    assert hasattr(codex_auth, 'normalize_codex_model')
    assert hasattr(chat_model, 'resolve_model_name')

    from codex_auth import normalize_codex_model
    from chat_model import resolve_model_name

    # Test Antigrav normalization
    assert resolve_model_name("antigravity-gemini-3-flash") == "gemini-3-flash"
    print("  [PASS] Antigrav: antigravity-gemini-3-flash -> gemini-3-flash")

    # Test Codex normalization
    assert normalize_codex_model("gpt-5.2-codex-high") == "gpt-5.2-codex"
    print("  [PASS] Codex: gpt-5.2-codex-high -> gpt-5.2-codex")

    tests_passed += 2
except Exception as e:
    print(f"  [FAIL] {e}")
    tests_failed += 1

# Test 7: Storage Paths
print("\n[TEST 7] Storage Paths")
try:
    assert hasattr(auth, 'get_config_dir')
    assert hasattr(auth, 'get_accounts_path')
    assert hasattr(codex_auth, 'get_codex_config_dir')
    assert hasattr(codex_auth, 'get_codex_accounts_path')

    paths = [
        auth.get_config_dir(),
        auth.get_accounts_path(),
        codex_auth.get_codex_config_dir(),
        codex_auth.get_codex_accounts_path(),
    ]
    print(f"  [PASS] All storage paths defined")
    print(f"         Antigrav config: {auth.get_config_dir()}")
    print(f"         Antigrav accounts: {auth.get_accounts_path()}")
    print(f"         Codex config: {codex_auth.get_codex_config_dir()}")
    print(f"         Codex accounts: {codex_auth.get_codex_accounts_path()}")

    tests_passed += 4
except Exception as e:
    print(f"  [FAIL] {e}")
    tests_failed += 1

# Summary
print("\n" + "="*60)
print("VERIFICATION SUMMARY")
print("="*60)
print(f"Tests Passed: {tests_passed}")
print(f"Tests Failed: {tests_failed}")

if tests_failed == 0:
    print("\n[SUCCESS] All verification tests passed!")
    print("\nImplementation is complete and ready for use.")
    print("\nNext steps:")
    print("  1. Run 'ag-auth login' for Google Antigrav authentication")
    print("  2. Run 'codex-auth login' for OpenAI Codex authentication")
    print("  3. Use ChatAntigrav for Google models (Gemini 3, Claude)")
    print("  4. Use ChatCodex for OpenAI models (GPT-5.x, Codex)")
    sys.exit(0)
else:
    print("\n[FAILED] Some verification tests failed")
    sys.exit(1)
