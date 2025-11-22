"""ReactAgent - A general-purpose AI Agent using the ReAct pattern.

This package provides a comprehensive AI agent implementation with:
- ReAct (Reasoning and Acting) pattern
- LangChain, LangGraph, and LangSmith integration
- Support for local models via OpenAI-compatible APIs
- Built-in tools for filesystem, glob, grep, and bash operations
- MCP server integration for custom tools
- Subagent system for task delegation
- Token tracking and context window management
"""

from .agent import ReactAgent
from .subagent import Subagent, SubagentResult
from .context_manager import (
    ContextManager,
    MessageRole,
    CompactionStrategy
)
from .token_tracker import TokenTracker, TokenUsage
from .mcp_client import MCPClient, MCPServerConfig, create_simple_tool
from .tools import (
    read_file,
    write_file,
    list_directory,
    glob_search,
    grep_search,
    run_bash_command,
)

__version__ = "0.1.0"

__all__ = [
    # Main agent
    "ReactAgent",

    # Subagents
    "Subagent",
    "SubagentResult",

    # Context management
    "ContextManager",
    "MessageRole",
    "CompactionStrategy",

    # Token tracking
    "TokenTracker",
    "TokenUsage",

    # MCP integration
    "MCPClient",
    "MCPServerConfig",
    "create_simple_tool",

    # Built-in tools
    "read_file",
    "write_file",
    "list_directory",
    "glob_search",
    "grep_search",
    "run_bash_command",
]
