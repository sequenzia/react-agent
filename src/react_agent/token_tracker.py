"""Token usage tracking for the ReactAgent."""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import tiktoken


@dataclass
class TokenUsage:
    """Represents token usage for a single interaction."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    context: Optional[str] = None


class TokenTracker:
    """Tracks token usage across agent interactions."""

    def __init__(self, model_name: str = "gpt-3.5-turbo", max_tokens: int = 4096):
        """Initialize the token tracker.

        Args:
            model_name: Name of the model for token encoding
            max_tokens: Maximum token limit for the context window
        """
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.usage_history: List[TokenUsage] = []

        # Initialize tokenizer
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            # Default to cl100k_base encoding if model not found
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        return len(self.encoding.encode(text))

    def count_messages_tokens(self, messages: List[Dict[str, str]]) -> int:
        """Count tokens in a list of messages.

        Args:
            messages: List of message dictionaries with 'role' and 'content'

        Returns:
            Total number of tokens
        """
        num_tokens = 0
        for message in messages:
            # Every message follows <|start|>{role/name}\n{content}<|end|>\n
            num_tokens += 4  # Message formatting tokens
            for key, value in message.items():
                num_tokens += self.count_tokens(str(value))
        num_tokens += 2  # Every reply is primed with <|start|>assistant
        return num_tokens

    def record_usage(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        context: Optional[str] = None
    ) -> TokenUsage:
        """Record token usage for an interaction.

        Args:
            prompt_tokens: Number of tokens in the prompt
            completion_tokens: Number of tokens in the completion
            context: Optional context description

        Returns:
            TokenUsage object
        """
        usage = TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            context=context
        )
        self.usage_history.append(usage)
        return usage

    def get_total_usage(self) -> Dict[str, int]:
        """Get total token usage across all interactions.

        Returns:
            Dictionary with total usage statistics
        """
        total_prompt = sum(u.prompt_tokens for u in self.usage_history)
        total_completion = sum(u.completion_tokens for u in self.usage_history)

        return {
            "total_prompt_tokens": total_prompt,
            "total_completion_tokens": total_completion,
            "total_tokens": total_prompt + total_completion,
            "interaction_count": len(self.usage_history),
            "max_tokens": self.max_tokens,
            "tokens_remaining": self.max_tokens - (total_prompt + total_completion)
        }

    def get_current_context_tokens(self, messages: List[Dict[str, str]]) -> int:
        """Get current token count for context window.

        Args:
            messages: Current conversation messages

        Returns:
            Current token count
        """
        return self.count_messages_tokens(messages)

    def is_near_limit(self, messages: List[Dict[str, str]], threshold: float = 0.8) -> bool:
        """Check if context window is near the token limit.

        Args:
            messages: Current conversation messages
            threshold: Percentage of max_tokens to consider "near limit" (0.0-1.0)

        Returns:
            True if near limit, False otherwise
        """
        current_tokens = self.get_current_context_tokens(messages)
        return current_tokens >= (self.max_tokens * threshold)

    def get_usage_summary(self) -> str:
        """Get a formatted summary of token usage.

        Returns:
            Formatted string with usage statistics
        """
        stats = self.get_total_usage()

        summary = f"""
Token Usage Summary
==================
Total Prompt Tokens:     {stats['total_prompt_tokens']:,}
Total Completion Tokens: {stats['total_completion_tokens']:,}
Total Tokens Used:       {stats['total_tokens']:,}
Max Tokens:              {stats['max_tokens']:,}
Tokens Remaining:        {stats['tokens_remaining']:,}
Total Interactions:      {stats['interaction_count']}

Usage Percentage:        {(stats['total_tokens'] / stats['max_tokens'] * 100):.2f}%
        """.strip()

        return summary

    def reset(self):
        """Reset token usage history."""
        self.usage_history.clear()
