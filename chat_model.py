"""
LangChain ChatModel for Antigravity API.

This module provides a LangChain BaseChatModel that communicates with Google's
Antigravity API, allowing access to Gemini 3 and Claude models.
"""

from __future__ import annotations

import json
import secrets
import time
from typing import Any, AsyncIterator, Literal

import httpx
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolCall,
    ToolMessage,
)
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from pydantic import Field

try:
    from . import auth as antigravity_auth
    from .auth import AntigravityAuth
except ImportError:  # pragma: no cover
    import auth as antigravity_auth  # type: ignore
    from auth import AntigravityAuth  # type: ignore
import constants
import schema


def is_claude_model(model: str) -> bool:
    """Check if model is a Claude model."""
    return "claude" in model.lower()


def is_thinking_model(model: str) -> bool:
    """Check if model supports extended thinking."""
    lower = model.lower()
    return "thinking" in lower or "gemini-3" in lower or "opus" in lower


def resolve_model_name(model: str) -> str:
    """Resolve model alias to actual API model name."""
    # Check direct mapping
    if model in constants.MODEL_MAPPINGS:
        return constants.MODEL_MAPPINGS[model]
    
    # Handle antigravity- prefix
    if model.startswith("antigravity-"):
        base = model[len("antigravity-"):]
        if base in constants.MODEL_MAPPINGS:
            return constants.MODEL_MAPPINGS[base]
    
    return model


def get_thinking_config(model: str) -> dict[str, Any] | None:
    """Get thinking configuration for a model."""
    lower = model.lower()

    if "claude" in lower and "thinking" in lower:
        if "low" in lower:
            budget = constants.THINKING_BUDGETS["low"]
        elif "high" in lower:
            budget = constants.THINKING_BUDGETS["high"]
        else:
            budget = constants.THINKING_BUDGETS["medium"]

        return {
            "thinking_budget": budget,
            "include_thoughts": True,
        }

    if "gemini-3" in lower:
        if "flash" in lower:
            level = "minimal"
        elif "high" in lower:
            level = "high"
        else:
            level = "low"
        return {
            "includeThoughts": True,
            "thinkingLevel": level,
        }

    return None


def get_header_style(model: str) -> Literal["antigravity", "gemini-cli"]:
    """Determine which header style to use based on model."""
    lower = model.lower()
    
    # Antigravity quota models
    if lower.startswith("antigravity-") or "claude" in lower:
        return "antigravity"
    
    # Gemini CLI quota models
    if "preview" in lower or lower.startswith("gemini-2.") or lower.startswith("gemini-3-"):
        return "gemini-cli"
    
    # Default to antigravity for gemini-3
    if "gemini-3" in lower:
        return "antigravity"
    
    return "gemini-cli"


class ChatAntigravity(BaseChatModel):
    """
    LangChain ChatModel for Antigravity API.
    
    Supports:
    - Gemini 3 models (Flash, Pro Low, Pro High)
    - Claude models (Sonnet 4.5, Opus 4.5)
    - Extended thinking for supported models
    - Tool/function calling
    
    Example:
        ```python
        from langchain_antigravity import ChatAntigravity
        
        chat = ChatAntigravity(model="antigravity-claude-sonnet-4-5")
        response = chat.invoke("Hello!")
        ```
    """
    
    model: str = Field(default="antigravity-gemini-3-flash")
    """Model name to use."""
    
    temperature: float | None = Field(default=None)
    """Sampling temperature."""
    
    max_output_tokens: int | None = Field(default=None)
    """Maximum output tokens."""
    
    auth: AntigravityAuth | None = Field(default=None, exclude=True)
    """Authentication state. If not provided, will load from storage."""
    
    project_id: str | None = Field(default=None)
    """Optional project ID override."""
    
    _tools: list[dict[str, Any]] = []
    """Bound tools."""
    
    @property
    def _llm_type(self) -> str:
        return "antigravity"
    
    @property
    def _identifying_params(self) -> dict[str, Any]:
        return {"model": self.model}
    
    def bind_tools(self, tools: list[Any]) -> "ChatAntigravity":
        """Bind tools to the model."""
        function_declarations = []
        
        for tool in tools:
            if hasattr(tool, "name") and hasattr(tool, "description"):
                # LangChain tool
                schema = {}
                if hasattr(tool, "args_schema") and tool.args_schema:
                    schema = tool.args_schema.model_json_schema()
                    schema = schema.clean_json_schema_for_antigravity(schema)
                
                # Add parameter signature to description
                description = tool.description
                if schema.get("properties"):
                    sig = schema.format_parameter_signature(
                        schema["properties"],
                        schema.get("required", []),
                    )
                    if sig:
                        description = f"{description}\n\nSTRICT PARAMETERS: {sig}."
                
                function_declarations.append({
                    "name": tool.name,
                    "description": description,
                    "parameters": schema,
                })
            elif isinstance(tool, dict):
                # Raw dict tool definition
                function_declarations.append(tool)
        
        new_model = self.model_copy()
        new_model._tools = function_declarations
        return new_model
    
    async def _ensure_auth(self) -> AntigravityAuth:
        """Ensure we have valid authentication."""
        if self.auth is None:
            self.auth = antigravity_auth.load_auth_from_storage()
        
        if self.auth is None:
            raise ValueError(
                "No Antigravity authentication found. "
                "Run 'opencode auth login' first or provide auth parameter."
            )
        
        if self.auth.is_expired():
            self.auth = await antigravity_auth.refresh_access_token(self.auth)
        
        return self.auth
    
    def _convert_messages(self, messages: list[BaseMessage]) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
        """Convert LangChain messages to Antigravity format."""
        contents = []
        system_instruction = None
        
        for msg in messages:
            if isinstance(msg, SystemMessage):
                system_instruction = {
                    "parts": [{"text": msg.content}]
                }
            elif isinstance(msg, HumanMessage):
                contents.append({
                    "role": "user",
                    "parts": self._convert_content(msg.content),
                })
            elif isinstance(msg, AIMessage):
                parts = []
                
                # Add text content
                if msg.content:
                    parts.append({"text": msg.content})
                
                # Add tool calls
                if msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        parts.append({
                            "functionCall": {
                                "name": tool_call["name"],
                                "args": tool_call["args"],
                                "id": tool_call["id"],
                            }
                        })
                
                contents.append({
                    "role": "model",
                    "parts": parts,
                })
            elif isinstance(msg, ToolMessage):
                contents.append({
                    "role": "user",
                    "parts": [{
                        "functionResponse": {
                            "name": msg.name or "unknown",
                            "response": {"result": msg.content},
                            "id": msg.tool_call_id,
                        }
                    }]
                })
        
        return contents, system_instruction
    
    def _convert_content(self, content: str | list[Any]) -> list[dict[str, Any]]:
        """Convert message content to parts."""
        if isinstance(content, str):
            return [{"text": content}]
        
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append({"text": item})
            elif isinstance(item, dict):
                if item.get("type") == "text":
                    parts.append({"text": item.get("text", "")})
                elif item.get("type") == "image_url":
                    # Handle image content
                    url = item.get("image_url", {}).get("url", "")
                    if url.startswith("data:"):
                        # Base64 image
                        mime_type = url.split(";")[0].split(":")[1]
                        data = url.split(",")[1]
                        parts.append({
                            "inlineData": {
                                "mimeType": mime_type,
                                "data": data,
                            }
                        })
        
        return parts if parts else [{"text": ""}]
    
    def _build_request_body(
        self,
        contents: list[dict[str, Any]],
        system_instruction: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Build the Antigravity request body."""
        effective_model = resolve_model_name(self.model)
        project_id = self.project_id or (self.auth.project_id if self.auth else None) or constants.ANTIGRAVITY_DEFAULT_PROJECT_ID
        
        # Build generation config
        generation_config: dict[str, Any] = {}
        if self.temperature is not None:
            generation_config["temperature"] = self.temperature
        if self.max_output_tokens is not None:
            generation_config["maxOutputTokens"] = self.max_output_tokens
        
        # Add thinking config if applicable
        thinking_config = get_thinking_config(self.model)
        if thinking_config:
            generation_config["thinkingConfig"] = thinking_config
        
        # Build request
        request: dict[str, Any] = {
            "contents": contents,
            "sessionId": f"session-{secrets.token_hex(16)}",
        }

        if generation_config:
            request["generationConfig"] = generation_config

        if system_instruction:
            # Add Claude tool hardening if tools are present
            if self._tools and is_claude_model(self.model):
                system_text = system_instruction["parts"][0].get("text", "")
                system_instruction = {
                    "parts": [{"text": f"{system_text}\n\n{constants.CLAUDE_TOOL_SYSTEM_INSTRUCTION}"}]
                }
            request["systemInstruction"] = system_instruction
        elif self._tools and is_claude_model(self.model):
            # Add tool hardening as system instruction if no system message
            request["systemInstruction"] = {
                "parts": [{"text": constants.CLAUDE_TOOL_SYSTEM_INSTRUCTION}]
            }

        if self._tools:
            request["tools"] = [{"functionDeclarations": self._tools}]
            # Claude requires VALIDATED mode for tool calling
            if is_claude_model(self.model):
                request["toolConfig"] = {
                    "functionCallingConfig": {
                        "mode": "VALIDATED",
                    }
                }

        # Wrap in Antigravity envelope
        return {
            "project": project_id,
            "model": effective_model,
            "request": request,
            "requestType": "agent",
            "userAgent": "antigravity",
            "requestId": f"agent-{secrets.token_hex(16)}",
        }
    
    def _parse_response(self, response_data: dict[str, Any]) -> AIMessage:
        """Parse Antigravity response into AIMessage."""
        # Unwrap response envelope
        inner = response_data.get("response", response_data)
        
        candidates = inner.get("candidates", [])
        if not candidates:
            return AIMessage(content="")
        
        candidate = candidates[0]
        content_obj = candidate.get("content", {})
        parts = content_obj.get("parts", [])
        
        text_parts = []
        tool_calls = []
        
        for part in parts:
            if "text" in part and not part.get("thought"):
                text_parts.append(part["text"])
            elif "functionCall" in part:
                fc = part["functionCall"]
                tool_calls.append(
                    ToolCall(
                        name=fc.get("name", ""),
                        args=fc.get("args", {}),
                        id=fc.get("id", ""),
                    )
                )
        
        content = "".join(text_parts)
        
        return AIMessage(content=content, tool_calls=tool_calls if tool_calls else [])
    
    async def _agenerate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate a response asynchronously."""
        auth = await self._ensure_auth()
        contents, system_instruction = self._convert_messages(messages)
        body = self._build_request_body(contents, system_instruction)
        
        header_style = get_header_style(self.model)
        headers = constants.ANTIGRAVITY_HEADERS if header_style == "antigravity" else constants.GEMINI_CLI_HEADERS
        headers = {
            **headers,
            "Authorization": f"Bearer {auth.access_token}",
            "Content-Type": "application/json",
        }

        if is_thinking_model(self.model) and is_claude_model(self.model):
            headers["anthropic-beta"] = "interleaved-thinking-2025-05-14"
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            for endpoint in constants.ANTIGRAVITY_ENDPOINT_FALLBACKS:
                url = f"{endpoint}/v1internal:generateContent"
                
                try:
                    response = await client.post(url, headers=headers, json=body)
                    
                    if response.status_code == 429:
                        # Rate limited - try next endpoint
                        continue
                    
                    if response.status_code >= 500:
                        # Server error - try next endpoint
                        continue
                    
                    response.raise_for_status()
                    
                    response_data = response.json()
                    message = self._parse_response(response_data)
                    
                    return ChatResult(generations=[ChatGeneration(message=message)])
                    
                except httpx.HTTPStatusError as e:
                    if e.response.status_code in (429, 500, 502, 503, 504):
                        continue
                    raise
                except httpx.RequestError:
                    continue
        
        raise RuntimeError("All Antigravity endpoints failed")
    
    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate a response synchronously."""
        import asyncio
        return asyncio.get_event_loop().run_until_complete(
            self._agenerate(messages, stop, run_manager, **kwargs)
        )
    
    async def _astream(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        """Stream a response asynchronously."""
        auth = await self._ensure_auth()
        contents, system_instruction = self._convert_messages(messages)
        body = self._build_request_body(contents, system_instruction)
        
        header_style = get_header_style(self.model)
        headers = constants.ANTIGRAVITY_HEADERS if header_style == "antigravity" else constants.GEMINI_CLI_HEADERS
        headers = {
            **headers,
            "Authorization": f"Bearer {auth.access_token}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }

        if is_thinking_model(self.model) and is_claude_model(self.model):
            headers["anthropic-beta"] = "interleaved-thinking-2025-05-14"
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            for endpoint in constants.ANTIGRAVITY_ENDPOINT_FALLBACKS:
                url = f"{endpoint}/v1internal:streamGenerateContent?alt=sse"
                
                try:
                    async with client.stream("POST", url, headers=headers, json=body) as response:
                        if response.status_code == 429 or response.status_code >= 500:
                            continue
                        
                        response.raise_for_status()
                        
                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                data = line[6:]
                                if data == "[DONE]":
                                    return
                                
                                try:
                                    chunk_data = json.loads(data)
                                    inner = chunk_data.get("response", chunk_data)
                                    candidates = inner.get("candidates", [])
                                    
                                    if candidates:
                                        parts = candidates[0].get("content", {}).get("parts", [])
                                        for part in parts:
                                            if "text" in part and not part.get("thought"):
                                                yield ChatGenerationChunk(
                                                    message=AIMessageChunk(content=part["text"])
                                                )
                                except json.JSONDecodeError:
                                    continue
                        
                        return
                        
                except httpx.HTTPStatusError as e:
                    if e.response.status_code in (429, 500, 502, 503, 504):
                        continue
                    raise
                except httpx.RequestError:
                    continue
        
        raise RuntimeError("All Antigravity endpoints failed")
