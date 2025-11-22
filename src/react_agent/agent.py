"""Main ReactAgent implementation using the ReAct pattern."""

from typing import List, Dict, Any, Optional, Union
import os
import logging
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent
from langchain.tools import BaseTool

from .context_manager import ContextManager, MessageRole, CompactionStrategy
from .token_tracker import TokenTracker
from .mcp_client import MCPClient
from .subagent import Subagent
from .tools import (
    read_file,
    write_file,
    list_directory,
    glob_search,
    grep_search,
    run_bash_command,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReactAgent:
    """A general-purpose AI Agent using the ReAct (Reasoning and Acting) pattern.

    This agent combines:
    - LangChain for LLM integration
    - LangGraph for workflow management (future enhancement)
    - LangSmith for monitoring and tracing
    - Built-in tools for filesystem, glob, grep, and bash operations
    - Support for custom tools and MCP servers
    - Subagent delegation for specialized tasks
    - Token tracking and context window management
    """

    def __init__(
        self,
        model_name: str = "gpt-3.5-turbo",
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        max_iterations: int = 15,
        enable_langsmith: bool = False,
        system_prompt: Optional[str] = None,
    ):
        """Initialize the ReactAgent.

        Args:
            model_name: Name of the model to use
            base_url: Base URL for OpenAI-compatible API (for local models)
            api_key: API key (can be placeholder for local models)
            temperature: Sampling temperature
            max_tokens: Maximum tokens for context window
            max_iterations: Maximum ReAct iterations
            enable_langsmith: Enable LangSmith tracing
            system_prompt: Custom system prompt (optional)
        """
        self.model_name = model_name
        self.max_iterations = max_iterations

        # Configure LangSmith
        if enable_langsmith:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"

        # Initialize LLM
        llm_kwargs = {
            "model": model_name,
            "temperature": temperature,
        }

        if base_url:
            llm_kwargs["base_url"] = base_url
        if api_key:
            llm_kwargs["api_key"] = api_key

        self.llm = ChatOpenAI(**llm_kwargs)

        # Initialize context and token management
        self.context_manager = ContextManager(
            max_tokens=max_tokens,
            compaction_strategy=CompactionStrategy(
                keep_first_n=2,
                keep_last_n=10,
                summarize_middle=True
            )
        )

        self.token_tracker = TokenTracker(
            model_name=model_name,
            max_tokens=max_tokens
        )

        # Initialize tools
        self.tools: List[BaseTool] = self._initialize_builtin_tools()

        # Initialize MCP client for custom tools
        self.mcp_client = MCPClient()

        # Subagents
        self.subagents: Dict[str, Subagent] = {}

        # System prompt
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.context_manager.add_message(MessageRole.SYSTEM, self.system_prompt)

        # Agent graph (will be created when needed)
        self._agent_graph = None

        logger.info(f"ReactAgent initialized with model: {model_name}")

    def _default_system_prompt(self) -> str:
        """Get the default system prompt for the ReAct agent.

        Returns:
            Default system prompt
        """
        return """You are a helpful AI assistant using the ReAct (Reasoning and Acting) pattern.

For each task:
1. Thought: Reason about what needs to be done
2. Action: Choose and execute a tool
3. Observation: Analyze the result
4. Repeat until the task is complete

You have access to various tools for:
- Reading and writing files
- Searching for files (glob patterns)
- Searching file contents (grep)
- Running bash commands

Always think step-by-step and use the appropriate tools to complete tasks effectively.
When you have enough information to answer the question, provide your final answer.
"""

    def _initialize_builtin_tools(self) -> List[BaseTool]:
        """Initialize built-in tools.

        Returns:
            List of built-in tools
        """
        return [
            read_file,
            write_file,
            list_directory,
            glob_search,
            grep_search,
            run_bash_command,
        ]

    def _get_agent_graph(self):
        """Get or create the agent graph.

        Returns:
            LangGraph agent graph instance
        """
        if self._agent_graph is None:
            # Combine built-in tools with MCP tools
            all_tools = self.tools + self.mcp_client.get_tools()

            # Create ReAct agent using LangGraph
            # The state_modifier adds the system prompt to messages
            self._agent_graph = create_react_agent(
                model=self.llm,
                tools=all_tools,
                state_modifier=self.system_prompt
            )

        return self._agent_graph

    def run(self, task: str, **kwargs) -> str:
        """Run the agent on a task.

        Args:
            task: Task description
            **kwargs: Additional arguments for the agent graph

        Returns:
            Agent's response
        """
        # Add task to context
        self.context_manager.add_message(MessageRole.USER, task)

        # Check if context needs compaction
        messages = self.context_manager.get_messages()
        if self.token_tracker.is_near_limit(messages, threshold=0.7):
            logger.info("Context near limit, performing compaction...")
            tokens_saved = self.context_manager.compact(self.token_tracker)
            logger.info(f"Compaction saved {tokens_saved} tokens")

        try:
            # Get agent graph
            agent = self._get_agent_graph()

            # Execute task using LangGraph message-based interface
            result = agent.invoke(
                {"messages": [{"role": "user", "content": task}]},
                **kwargs
            )

            # Extract response from the last message
            # LangGraph returns messages in the state
            response_messages = result.get("messages", [])
            if response_messages:
                # Get the last AI message
                last_message = response_messages[-1]
                response = last_message.content if hasattr(last_message, 'content') else str(last_message)
            else:
                response = str(result)

            # Add response to context
            self.context_manager.add_message(MessageRole.ASSISTANT, response)

            # Track tokens (approximation)
            prompt_tokens = self.token_tracker.count_messages_tokens(messages)
            completion_tokens = self.token_tracker.count_tokens(response)
            self.token_tracker.record_usage(prompt_tokens, completion_tokens, context=task)

            return response

        except Exception as e:
            error_msg = f"Error executing task: {str(e)}"
            logger.error(error_msg)
            self.context_manager.add_message(MessageRole.ASSISTANT, error_msg)
            return error_msg

    def add_tool(self, tool: BaseTool):
        """Add a custom tool to the agent.

        Args:
            tool: LangChain BaseTool instance
        """
        self.tools.append(tool)
        self._agent_graph = None  # Reset graph to include new tool
        logger.info(f"Added tool: {tool.name}")

    def add_mcp_server(self, url: str, name: Optional[str] = None, api_key: Optional[str] = None):
        """Add an MCP server for custom tools.

        Args:
            url: URL of the MCP server
            name: Optional name for the server
            api_key: Optional API key
        """
        success = self.mcp_client.add_server(url, name, api_key)
        if success:
            self._agent_graph = None  # Reset graph to include new tools
            logger.info(f"Added MCP server: {name or url}")
        return success

    def create_subagent(
        self,
        name: str,
        system_prompt: str,
        tools: Optional[List[BaseTool]] = None,
        max_tokens: int = 4096
    ) -> Subagent:
        """Create a subagent for specialized tasks.

        Args:
            name: Name of the subagent
            system_prompt: System prompt defining the subagent's role
            tools: Optional list of tools (defaults to parent's tools)
            max_tokens: Maximum tokens for subagent context

        Returns:
            Subagent instance
        """
        if tools is None:
            tools = self.tools.copy()

        subagent = Subagent(
            name=name,
            system_prompt=system_prompt,
            llm=self.llm,
            tools=tools,
            max_tokens=max_tokens,
            parent_agent=self
        )

        self.subagents[name] = subagent
        logger.info(f"Created subagent: {name}")

        return subagent

    def get_subagent(self, name: str) -> Optional[Subagent]:
        """Get a subagent by name.

        Args:
            name: Name of the subagent

        Returns:
            Subagent instance or None
        """
        return self.subagents.get(name)

    def show_token_usage(self) -> str:
        """Show current token usage.

        Returns:
            Formatted token usage summary
        """
        summary = self.token_tracker.get_usage_summary()
        print(summary)
        return summary

    def show_context_state(self) -> str:
        """Show current context window state.

        Returns:
            Formatted context state summary
        """
        summary = self.context_manager.get_state_summary(self.token_tracker)
        print(summary)
        return summary

    def get_token_usage(self) -> Dict[str, int]:
        """Get token usage statistics.

        Returns:
            Dictionary with token usage stats
        """
        return self.token_tracker.get_total_usage()

    def get_context_state(self) -> Dict[str, Any]:
        """Get context window state.

        Returns:
            Dictionary with context state
        """
        return self.context_manager.get_state()

    def reset(self):
        """Reset the agent's context and token tracking."""
        self.context_manager.clear()
        self.context_manager.add_message(MessageRole.SYSTEM, self.system_prompt)
        self.token_tracker.reset()
        logger.info("Agent reset")

    def export_state(self, filepath: str):
        """Export agent state to a file.

        Args:
            filepath: Path to save state
        """
        # Export context
        context_file = filepath.replace(".json", "_context.json")
        self.context_manager.export_context(context_file)

        # Export full state
        import json
        state = {
            "model_name": self.model_name,
            "system_prompt": self.system_prompt,
            "token_usage": self.token_tracker.get_total_usage(),
            "context_state": self.context_manager.get_state(),
            "subagents": list(self.subagents.keys()),
            "mcp_servers": self.mcp_client.list_servers(),
            "timestamp": datetime.now().isoformat()
        }

        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)

        logger.info(f"State exported to {filepath}")
