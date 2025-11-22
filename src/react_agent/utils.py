"""Utility functions and helpers for the ReactAgent."""

import os
from typing import Dict, Any, Optional
from pathlib import Path
import json


def load_env_config(env_file: str = ".env") -> Dict[str, str]:
    """Load configuration from .env file.

    Args:
        env_file: Path to .env file

    Returns:
        Dictionary of environment variables
    """
    config = {}

    env_path = Path(env_file)
    if not env_path.exists():
        return config

    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()

    return config


def create_agent_from_config(config_file: str = ".env") -> "ReactAgent":
    """Create a ReactAgent from configuration file.

    Args:
        config_file: Path to configuration file

    Returns:
        Configured ReactAgent instance
    """
    from .agent import ReactAgent

    # Load config
    config = load_env_config(config_file)

    # Extract agent parameters
    agent_params = {
        "model_name": config.get("MODEL_NAME", "gpt-3.5-turbo"),
        "base_url": config.get("OPENAI_API_BASE"),
        "api_key": config.get("OPENAI_API_KEY", "not-needed"),
        "temperature": float(config.get("TEMPERATURE", "0.7")),
        "max_tokens": int(config.get("MAX_TOKENS", "4096")),
        "enable_langsmith": config.get("LANGCHAIN_TRACING_V2", "false").lower() == "true",
    }

    # Set LangSmith env vars if enabled
    if agent_params["enable_langsmith"]:
        if "LANGCHAIN_API_KEY" in config:
            os.environ["LANGCHAIN_API_KEY"] = config["LANGCHAIN_API_KEY"]
        if "LANGCHAIN_ENDPOINT" in config:
            os.environ["LANGCHAIN_ENDPOINT"] = config["LANGCHAIN_ENDPOINT"]
        if "LANGCHAIN_PROJECT" in config:
            os.environ["LANGCHAIN_PROJECT"] = config["LANGCHAIN_PROJECT"]

    return ReactAgent(**agent_params)


def format_tool_output(output: str, max_length: int = 1000) -> str:
    """Format and truncate tool output for display.

    Args:
        output: Raw tool output
        max_length: Maximum length for output

    Returns:
        Formatted output string
    """
    if len(output) <= max_length:
        return output

    truncated = output[:max_length]
    return f"{truncated}\n\n... [Output truncated - {len(output)} total characters]"


def estimate_cost(
    prompt_tokens: int,
    completion_tokens: int,
    model: str = "gpt-3.5-turbo"
) -> float:
    """Estimate cost for API usage.

    Args:
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens
        model: Model name

    Returns:
        Estimated cost in USD

    Note:
        Prices are approximate and may not reflect actual costs.
        For local models, this returns 0.0.
    """
    # Pricing as of 2024 (USD per 1K tokens)
    pricing = {
        "gpt-4": {"prompt": 0.03, "completion": 0.06},
        "gpt-4-turbo": {"prompt": 0.01, "completion": 0.03},
        "gpt-3.5-turbo": {"prompt": 0.0005, "completion": 0.0015},
    }

    # Return 0 for local models or unknown models
    if model not in pricing:
        return 0.0

    rates = pricing[model]
    prompt_cost = (prompt_tokens / 1000) * rates["prompt"]
    completion_cost = (completion_tokens / 1000) * rates["completion"]

    return prompt_cost + completion_cost


def save_conversation(
    messages: list,
    filepath: str,
    metadata: Optional[Dict[str, Any]] = None
):
    """Save conversation history to a file.

    Args:
        messages: List of conversation messages
        filepath: Path to save the conversation
        metadata: Optional metadata to include
    """
    data = {
        "messages": messages,
        "metadata": metadata or {},
        "message_count": len(messages)
    }

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def load_conversation(filepath: str) -> Dict[str, Any]:
    """Load conversation history from a file.

    Args:
        filepath: Path to the conversation file

    Returns:
        Dictionary with messages and metadata
    """
    with open(filepath, 'r') as f:
        return json.load(f)


class AgentLogger:
    """Simple logger for agent activities."""

    def __init__(self, log_file: Optional[str] = None, verbose: bool = True):
        """Initialize the logger.

        Args:
            log_file: Optional file to write logs to
            verbose: Whether to print to console
        """
        self.log_file = log_file
        self.verbose = verbose
        self.logs = []

    def log(self, message: str, level: str = "INFO"):
        """Log a message.

        Args:
            message: Message to log
            level: Log level (INFO, WARNING, ERROR)
        """
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"

        self.logs.append(log_entry)

        if self.verbose:
            print(log_entry)

        if self.log_file:
            with open(self.log_file, 'a') as f:
                f.write(log_entry + "\n")

    def info(self, message: str):
        """Log an info message."""
        self.log(message, "INFO")

    def warning(self, message: str):
        """Log a warning message."""
        self.log(message, "WARNING")

    def error(self, message: str):
        """Log an error message."""
        self.log(message, "ERROR")

    def get_logs(self) -> list:
        """Get all log entries.

        Returns:
            List of log entries
        """
        return self.logs.copy()

    def save_logs(self, filepath: str):
        """Save logs to a file.

        Args:
            filepath: Path to save logs
        """
        with open(filepath, 'w') as f:
            f.write("\n".join(self.logs))
