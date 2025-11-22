"""Subagent implementation for delegating specialized tasks."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

from .context_manager import ContextManager, MessageRole, CompactionStrategy
from .token_tracker import TokenTracker


@dataclass
class SubagentResult:
    """Result from a subagent execution."""

    success: bool
    result: str
    summary: str
    token_usage: Dict[str, int]
    execution_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class Subagent:
    """A subagent for handling specialized tasks with independent context."""

    def __init__(
        self,
        name: str,
        system_prompt: str,
        llm,  # LangChain LLM instance
        tools: Optional[List] = None,
        max_tokens: int = 4096,
        max_iterations: int = 10,
        parent_agent: Optional[Any] = None
    ):
        """Initialize a subagent.

        Args:
            name: Name of the subagent
            system_prompt: System prompt defining the subagent's role
            llm: LangChain LLM instance
            tools: List of tools available to the subagent
            max_tokens: Maximum tokens for context window
            max_iterations: Maximum ReAct iterations
            parent_agent: Reference to parent agent (optional)
        """
        self.name = name
        self.system_prompt = system_prompt
        self.llm = llm
        self.tools = tools or []
        self.max_iterations = max_iterations
        self.parent_agent = parent_agent

        # Independent context and token tracking
        self.context_manager = ContextManager(
            max_tokens=max_tokens,
            compaction_strategy=CompactionStrategy(
                keep_first_n=1,  # Just the system prompt
                keep_last_n=5,   # Recent context
                summarize_middle=True
            )
        )

        self.token_tracker = TokenTracker(
            model_name=getattr(llm, 'model_name', 'gpt-3.5-turbo'),
            max_tokens=max_tokens
        )

        # Initialize context with system prompt
        self.context_manager.add_message(
            MessageRole.SYSTEM,
            system_prompt
        )

        # Execution metadata
        self.created_at = datetime.now()
        self.execution_count = 0
        self.total_tokens_used = 0

    def run(self, task: str) -> SubagentResult:
        """Execute a task using the ReAct pattern.

        Args:
            task: Task description for the subagent

        Returns:
            SubagentResult with execution details
        """
        start_time = datetime.now()
        self.execution_count += 1

        # Add user task to context
        self.context_manager.add_message(MessageRole.USER, task)

        try:
            # Execute ReAct loop
            result = self._react_loop(task)

            # Generate summary
            summary = self._generate_summary()

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()

            # Get token usage
            token_usage = self.token_tracker.get_total_usage()
            self.total_tokens_used += token_usage["total_tokens"]

            return SubagentResult(
                success=True,
                result=result,
                summary=summary,
                token_usage=token_usage,
                execution_time=execution_time,
                metadata={
                    "iterations": self.execution_count,
                    "context_compactions": self.context_manager.compaction_count
                }
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()

            return SubagentResult(
                success=False,
                result=f"Error: {str(e)}",
                summary=f"Subagent {self.name} encountered an error: {str(e)}",
                token_usage=self.token_tracker.get_total_usage(),
                execution_time=execution_time,
                metadata={"error": str(e)}
            )

    def _react_loop(self, task: str) -> str:
        """Execute the ReAct (Reasoning and Acting) loop.

        Args:
            task: Task to execute

        Returns:
            Final result
        """
        iteration = 0
        final_answer = None

        while iteration < self.max_iterations and final_answer is None:
            iteration += 1

            # Check if context needs compaction
            messages = self.context_manager.get_messages()
            if self.token_tracker.is_near_limit(messages, threshold=0.7):
                tokens_saved = self.context_manager.compact(self.token_tracker)
                messages = self.context_manager.get_messages()

            # Get LLM response (this is simplified - in real implementation,
            # you would use LangChain's agent executor or LangGraph)
            # For now, this is a placeholder that shows the structure

            # In a real implementation with LangChain:
            # 1. Create agent with tools
            # 2. Execute agent.invoke(messages)
            # 3. Parse response for thoughts, actions, and observations
            # 4. Continue loop until final answer

            # Placeholder response
            response_text = f"Iteration {iteration}: Processing task '{task}'"

            # Track tokens (placeholder - would come from actual LLM response)
            prompt_tokens = self.token_tracker.count_messages_tokens(messages)
            completion_tokens = self.token_tracker.count_tokens(response_text)
            self.token_tracker.record_usage(
                prompt_tokens,
                completion_tokens,
                context=f"Subagent {self.name} iteration {iteration}"
            )

            # Add response to context
            self.context_manager.add_message(MessageRole.ASSISTANT, response_text)

            # For this placeholder, we'll complete after first iteration
            final_answer = response_text

        return final_answer or "Max iterations reached without final answer"

    def _generate_summary(self) -> str:
        """Generate a summary of the subagent's execution for the parent agent.

        Returns:
            Summary string
        """
        messages = self.context_manager.get_messages()
        token_usage = self.token_tracker.get_total_usage()

        # Extract key information
        user_messages = [m for m in messages if m["role"] == MessageRole.USER.value]
        assistant_messages = [m for m in messages if m["role"] == MessageRole.ASSISTANT.value]

        summary_parts = [
            f"Subagent: {self.name}",
            f"Task: {user_messages[-1]['content'] if user_messages else 'N/A'}",
            f"Messages exchanged: {len(messages)}",
            f"Tokens used: {token_usage['total_tokens']}",
            f"Context compactions: {self.context_manager.compaction_count}",
        ]

        # Add last assistant response
        if assistant_messages:
            last_response = assistant_messages[-1]["content"]
            if len(last_response) > 200:
                last_response = last_response[:200] + "..."
            summary_parts.append(f"Last response: {last_response}")

        return "\n".join(summary_parts)

    def get_summary(self) -> str:
        """Get a summary of the subagent's state.

        Returns:
            Formatted summary string
        """
        return self._generate_summary()

    def get_context_state(self) -> Dict[str, Any]:
        """Get the current context state.

        Returns:
            Context state dictionary
        """
        return self.context_manager.get_state()

    def get_token_usage(self) -> Dict[str, int]:
        """Get token usage statistics.

        Returns:
            Token usage dictionary
        """
        return self.token_tracker.get_total_usage()

    def reset(self):
        """Reset the subagent's context and token tracking."""
        # Clear context but keep system prompt
        self.context_manager.clear()
        self.context_manager.add_message(MessageRole.SYSTEM, self.system_prompt)

        # Reset token tracker
        self.token_tracker.reset()

        # Reset metadata
        self.execution_count = 0
        self.total_tokens_used = 0

    def export_state(self, filepath: str):
        """Export subagent state to a file.

        Args:
            filepath: Path to save state
        """
        state = {
            "name": self.name,
            "system_prompt": self.system_prompt,
            "created_at": self.created_at.isoformat(),
            "execution_count": self.execution_count,
            "total_tokens_used": self.total_tokens_used,
            "context": self.context_manager.get_messages(),
            "token_usage": self.token_tracker.get_total_usage(),
            "context_state": self.context_manager.get_state()
        }

        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
