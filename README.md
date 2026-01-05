# LangChain Antigravity

Access **Gemini 3** and **Claude** models via Google's Antigravity API using LangChain.

This package provides a native Python LangChain `ChatModel` that authenticates with Google OAuth, allowing you to use models like `gemini-3-flash`, `gemini-3-pro-high`, and `claude-sonnet-4-5` in your LangChain applications.

## Installation

install from source:

```bash
cd langchain_antigravity
pip install -e .
```

## Quick Start

### 1. Authenticate

```bash
ag-auth login
```

This opens your browser to sign in with Google. Credentials are stored locally.

### 2. Use in LangChain

```python
from langchain_antigravity import ChatAntigravity

chat = ChatAntigravity(model="antigravity-gemini-3-flash")
response = chat.invoke("Hello! What's 2 + 2?")
print(response.content)
```

## Available Models

### Gemini 3 Models

| Model | Description |
|-------|-------------|
| `antigravity-gemini-3-flash` | Fast, efficient model with thinking |
| `antigravity-gemini-3-pro-low` | Pro model with low thinking budget |
| `antigravity-gemini-3-pro-high` | Pro model with high thinking budget |

### Claude Models

| Model | Description |
|-------|-------------|
| `antigravity-claude-sonnet-4-5` | Claude Sonnet 4.5 |
| `antigravity-claude-sonnet-4-5-thinking-low` | Sonnet with 8K thinking budget |
| `antigravity-claude-sonnet-4-5-thinking-medium` | Sonnet with 16K thinking budget |
| `antigravity-claude-sonnet-4-5-thinking-high` | Sonnet with 32K thinking budget |
| `antigravity-claude-opus-4-5-thinking-low` | Opus with 8K thinking budget |
| `antigravity-claude-opus-4-5-thinking-medium` | Opus with 16K thinking budget |
| `antigravity-claude-opus-4-5-thinking-high` | Opus with 32K thinking budget |

## Features

### Streaming

```python
from langchain_antigravity import ChatAntigravity

chat = ChatAntigravity(model="antigravity-gemini-3-flash")

for chunk in chat.stream("Count from 1 to 5"):
    print(chunk.content, end="", flush=True)
```

### Tool Calling

```python
from langchain_antigravity import ChatAntigravity

weather_tool = {
    "name": "get_weather",
    "description": "Get weather for a location",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {"type": "string", "description": "City name"}
        },
        "required": ["location"]
    }
}

chat = ChatAntigravity(model="antigravity-gemini-3-flash").bind_tools([weather_tool])
response = chat.invoke("What's the weather in Paris?")

if response.tool_calls:
    for tc in response.tool_calls:
        print(f"Tool: {tc['name']}, Args: {tc['args']}")
```

### Multi-Account Support

```bash
# Add another account
ag-auth login

# List accounts
ag-auth accounts

# Switch active account
ag-auth accounts --set user@gmail.com

# Remove account
ag-auth logout user@gmail.com
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `ag-auth login` | Authenticate with Google |
| `ag-auth logout [email]` | Remove an account |
| `ag-auth accounts` | List authenticated accounts |
| `ag-auth accounts --set EMAIL` | Set active account |
| `ag-auth status` | Check authentication status |

## Configuration

Credentials are stored in:
- **Windows**: `%APPDATA%\langchain-antigravity\accounts.json`
- **Linux/Mac**: `~/.config/langchain-antigravity/accounts.json`

## API Reference

### ChatAntigravity

```python
ChatAntigravity(
    model: str = "antigravity-gemini-3-flash",  # Model name
    temperature: float = None,                   # Sampling temperature
    max_output_tokens: int = None,               # Max output tokens
    auth: AntigravityAuth = None,                # Optional auth override
    project_id: str = None,                      # Optional project ID
)
```

### Methods

- `invoke(messages)` - Generate a response
- `stream(messages)` - Stream a response
- `bind_tools(tools)` - Bind tools for function calling

## Migration from OpenCode

If you previously used `opencode auth login`, this package can read those credentials. They're stored in the same format, just in a different location. To migrate:

```bash
# Your existing opencode credentials will be auto-detected
ag-auth status

# Or login fresh
ag-auth login
```

## Credits

This package is a Python port of the authentication and API logic from [opencode-antigravity-auth](https://github.com/NoeFabris/opencode-antigravity-auth) by [@NoeFabris](https://github.com/NoeFabris).

The original TypeScript plugin enables OpenCode to authenticate with Google's Antigravity API. This Python package brings the same functionality to LangChain applications.

## License

MIT

## Disclaimer

- This is an independent open-source project, not affiliated with Google
- "Antigravity", "Gemini", and "Google" are trademarks of Google LLC
- Use responsibly and in accordance with Google's terms of service
