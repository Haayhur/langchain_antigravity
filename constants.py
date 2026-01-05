"""
Constants for Antigravity OAuth and API integration.

Based on opencode-antigravity-auth by NoeFabris:
https://github.com/NoeFabris/opencode-antigravity-auth
"""

ANTIGRAVITY_CLIENT_ID = "1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com"
ANTIGRAVITY_CLIENT_SECRET = "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"

ANTIGRAVITY_SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/cclog",
    "https://www.googleapis.com/auth/experimentsandconfigs",
]

ANTIGRAVITY_REDIRECT_URI = "http://localhost:51121/oauth-callback"

ANTIGRAVITY_ENDPOINT_DAILY = "https://daily-cloudcode-pa.sandbox.googleapis.com"
ANTIGRAVITY_ENDPOINT_AUTOPUSH = "https://autopush-cloudcode-pa.sandbox.googleapis.com"
ANTIGRAVITY_ENDPOINT_PROD = "https://cloudcode-pa.googleapis.com"

ANTIGRAVITY_ENDPOINT_FALLBACKS = [
    ANTIGRAVITY_ENDPOINT_DAILY,
    ANTIGRAVITY_ENDPOINT_AUTOPUSH,
    ANTIGRAVITY_ENDPOINT_PROD,
]

ANTIGRAVITY_LOAD_ENDPOINTS = [
    ANTIGRAVITY_ENDPOINT_PROD,
    ANTIGRAVITY_ENDPOINT_DAILY,
    ANTIGRAVITY_ENDPOINT_AUTOPUSH,
]

ANTIGRAVITY_ENDPOINT = ANTIGRAVITY_ENDPOINT_DAILY
GEMINI_CLI_ENDPOINT = ANTIGRAVITY_ENDPOINT_PROD

ANTIGRAVITY_DEFAULT_PROJECT_ID = "rising-fact-p41fc"

ANTIGRAVITY_HEADERS = {
    "User-Agent": "antigravity/1.11.5 windows/amd64",
    "X-Goog-Api-Client": "google-cloud-sdk vscode_cloudshelleditor/0.1",
    "Client-Metadata": '{"ideType":"IDE_UNSPECIFIED","platform":"PLATFORM_UNSPECIFIED","pluginType":"GEMINI"}',
}

GEMINI_CLI_HEADERS = {
    "User-Agent": "google-api-nodejs-client/9.15.1",
    "X-Goog-Api-Client": "gl-node/22.17.0",
    "Client-Metadata": "ideType=IDE_UNSPECIFIED,platform=PLATFORM_UNSPECIFIED,pluginType=GEMINI",
}

DEFAULT_THINKING_BUDGET = 16000

EMPTY_SCHEMA_PLACEHOLDER_NAME = "_placeholder"
EMPTY_SCHEMA_PLACEHOLDER_DESCRIPTION = "Placeholder. Always pass true."

CLAUDE_TOOL_SYSTEM_INSTRUCTION = """CRITICAL TOOL USAGE INSTRUCTIONS:
You are operating in a custom environment where tool definitions differ from your training data.
You MUST follow these rules strictly:

1. DO NOT use your internal training data to guess tool parameters
2. ONLY use the exact parameter structure defined in the tool schema
3. Parameter names in schemas are EXACT - do not substitute with similar names from your training
4. Array parameters have specific item types - check the schema's 'items' field for the exact structure
5. When you see "STRICT PARAMETERS" in a tool description, those type definitions override any assumptions
6. Tool use in agentic workflows is REQUIRED - you must call tools with the exact parameters specified

If you are unsure about a tool's parameters, YOU MUST read the schema definition carefully."""

MODEL_MAPPINGS = {
    "antigravity-gemini-3-flash": "gemini-3-flash",
    "antigravity-gemini-3-pro-low": "gemini-3-pro-low",
    "antigravity-gemini-3-pro-high": "gemini-3-pro-high",
    "antigravity-claude-sonnet-4-5": "claude-sonnet-4-5",
    "antigravity-claude-sonnet-4-5-thinking-low": "claude-sonnet-4-5-thinking",
    "antigravity-claude-sonnet-4-5-thinking-medium": "claude-sonnet-4-5-thinking",
    "antigravity-claude-sonnet-4-5-thinking-high": "claude-sonnet-4-5-thinking",
    "antigravity-claude-opus-4-5-thinking-low": "claude-opus-4-5-thinking",
    "antigravity-claude-opus-4-5-thinking-medium": "claude-opus-4-5-thinking",
    "antigravity-claude-opus-4-5-thinking-high": "claude-opus-4-5-thinking",
    "gemini-2.5-flash": "gemini-2.5-flash-preview-05-20",
    "gemini-2.5-pro": "gemini-2.5-pro-preview-05-06",
    "gemini-3-flash-preview": "gemini-3.0-flash-preview",
    "gemini-3-pro-preview": "gemini-3.0-pro-preview",
}

THINKING_BUDGETS = {
    "low": 8000,
    "medium": 16000,
    "high": 32000,
}

GEMINI_THINKING_LEVELS = {
    "flash": "THINKING_LEVEL_LOW",
    "low": "THINKING_LEVEL_LOW",
    "high": "THINKING_LEVEL_MAX",
}
