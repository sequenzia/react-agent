"""Context window management and compaction for the ReactAgent."""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json


class MessageRole(str, Enum):
    """Message roles in the conversation."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class CompactionStrategy:
    """Configuration for context compaction."""

    # Keep first N messages (usually system prompt + initial context)
    keep_first_n: int = 2

    # Keep last N messages (recent context)
    keep_last_n: int = 10

    # Summarize middle messages
    summarize_middle: bool = True

    # Maximum tokens for summary
    summary_max_tokens: int = 500


class ContextManager:
    """Manages conversation context and performs compaction when needed."""

    def __init__(
        self,
        max_tokens: int = 4096,
        compaction_strategy: Optional[CompactionStrategy] = None
    ):
        """Initialize the context manager.

        Args:
            max_tokens: Maximum tokens allowed in context
            compaction_strategy: Strategy for context compaction
        """
        self.max_tokens = max_tokens
        self.messages: List[Dict[str, Any]] = []
        self.compaction_strategy = compaction_strategy or CompactionStrategy()
        self.compaction_count = 0
        self.metadata: Dict[str, Any] = {
            "total_messages": 0,
            "compactions": 0,
            "tokens_saved": 0
        }

    def add_message(
        self,
        role: MessageRole,
        content: str,
        name: Optional[str] = None,
        tool_calls: Optional[List[Dict]] = None,
        tool_call_id: Optional[str] = None
    ):
        """Add a message to the context.

        Args:
            role: Role of the message sender
            content: Content of the message
            name: Optional name (for tool messages)
            tool_calls: Optional tool calls (for assistant messages)
            tool_call_id: Optional tool call ID (for tool messages)
        """
        message = {"role": role.value, "content": content}

        if name:
            message["name"] = name
        if tool_calls:
            message["tool_calls"] = tool_calls
        if tool_call_id:
            message["tool_call_id"] = tool_call_id

        self.messages.append(message)
        self.metadata["total_messages"] += 1

    def get_messages(self) -> List[Dict[str, Any]]:
        """Get all messages in the context.

        Returns:
            List of message dictionaries
        """
        return self.messages.copy()

    def clear(self):
        """Clear all messages from context."""
        self.messages.clear()

    def compact(self, token_tracker) -> int:
        """Compact the context window by summarizing or removing old messages.

        Args:
            token_tracker: TokenTracker instance for counting tokens

        Returns:
            Number of tokens saved
        """
        if len(self.messages) <= (
            self.compaction_strategy.keep_first_n + self.compaction_strategy.keep_last_n
        ):
            return 0  # Not enough messages to compact

        original_tokens = token_tracker.count_messages_tokens(self.messages)

        # Keep first N messages (system prompt, etc.)
        first_messages = self.messages[:self.compaction_strategy.keep_first_n]

        # Keep last N messages (recent context)
        last_messages = self.messages[-self.compaction_strategy.keep_last_n:]

        # Get middle messages to summarize
        middle_messages = self.messages[
            self.compaction_strategy.keep_first_n:-self.compaction_strategy.keep_last_n
        ]

        # Create summary of middle messages
        if self.compaction_strategy.summarize_middle and middle_messages:
            summary = self._summarize_messages(middle_messages)
            summary_message = {
                "role": MessageRole.SYSTEM.value,
                "content": f"[Context Summary - {len(middle_messages)} messages compressed]\n{summary}"
            }

            # Reconstruct messages with summary
            self.messages = first_messages + [summary_message] + last_messages
        else:
            # Just keep first and last
            self.messages = first_messages + last_messages

        new_tokens = token_tracker.count_messages_tokens(self.messages)
        tokens_saved = original_tokens - new_tokens

        self.compaction_count += 1
        self.metadata["compactions"] += 1
        self.metadata["tokens_saved"] += tokens_saved

        return tokens_saved

    def _summarize_messages(self, messages: List[Dict[str, Any]]) -> str:
        """Create a summary of messages.

        Args:
            messages: Messages to summarize

        Returns:
            Summary string
        """
        summary_parts = []

        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            # Truncate long content
            if len(content) > 200:
                content = content[:200] + "..."

            if role == MessageRole.USER.value:
                summary_parts.append(f"User asked: {content}")
            elif role == MessageRole.ASSISTANT.value:
                if "tool_calls" in msg:
                    tools = [tc.get("function", {}).get("name", "unknown")
                            for tc in msg.get("tool_calls", [])]
                    summary_parts.append(f"Assistant used tools: {', '.join(tools)}")
                else:
                    summary_parts.append(f"Assistant: {content}")
            elif role == MessageRole.TOOL.value:
                tool_name = msg.get("name", "unknown")
                summary_parts.append(f"Tool {tool_name} executed")

        return "\n".join(summary_parts)

    def get_state(self) -> Dict[str, Any]:
        """Get current state of the context window.

        Returns:
            Dictionary with context state information
        """
        return {
            "message_count": len(self.messages),
            "total_messages_seen": self.metadata["total_messages"],
            "compaction_count": self.compaction_count,
            "tokens_saved": self.metadata["tokens_saved"],
            "max_tokens": self.max_tokens,
            "compaction_strategy": {
                "keep_first_n": self.compaction_strategy.keep_first_n,
                "keep_last_n": self.compaction_strategy.keep_last_n,
                "summarize_middle": self.compaction_strategy.summarize_middle
            }
        }

    def get_state_summary(self, token_tracker) -> str:
        """Get a formatted summary of context state.

        Args:
            token_tracker: TokenTracker for current token count

        Returns:
            Formatted string with context state
        """
        state = self.get_state()
        current_tokens = token_tracker.count_messages_tokens(self.messages)
        usage_pct = (current_tokens / self.max_tokens) * 100

        summary = f"""
Context Window State
===================
Current Messages:        {state['message_count']}
Total Messages Seen:     {state['total_messages_seen']}
Current Tokens:          {current_tokens:,} / {state['max_tokens']:,}
Usage Percentage:        {usage_pct:.2f}%
Compactions Performed:   {state['compaction_count']}
Tokens Saved:            {state['tokens_saved']:,}

Compaction Strategy:
  Keep First N:          {state['compaction_strategy']['keep_first_n']}
  Keep Last N:           {state['compaction_strategy']['keep_last_n']}
  Summarize Middle:      {state['compaction_strategy']['summarize_middle']}
        """.strip()

        return summary

    def export_context(self, filepath: str):
        """Export context to a JSON file.

        Args:
            filepath: Path to save the context
        """
        data = {
            "messages": self.messages,
            "metadata": self.metadata,
            "state": self.get_state()
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def import_context(self, filepath: str):
        """Import context from a JSON file.

        Args:
            filepath: Path to load the context from
        """
        with open(filepath, 'r') as f:
            data = json.load(f)

        self.messages = data.get("messages", [])
        self.metadata = data.get("metadata", {})
        if "state" in data:
            self.compaction_count = data["state"].get("compaction_count", 0)
