# ReAct AI Agent

A general-purpose AI Agent implementation using the ReAct (Reasoning and Acting) pattern with LangChain, LangGraph, and LangSmith.

## Features

- **ReAct Pattern**: Combines reasoning and acting for intelligent task execution
- **LangChain & LangGraph**: Built on industry-standard frameworks
- **LangSmith Integration**: Track and monitor agent performance
- **Local Model Support**: Works with locally hosted models using OpenAI-compatible APIs
- **Built-in Tools**:
  - Filesystem operations (read/write)
  - Glob pattern matching
  - Grep text search
  - Bash command execution
- **Custom Tool Support**: Integrate MCP servers and custom tools
- **Subagent System**: Create specialized subagents with independent context
- **Token Tracking**: Monitor token usage across conversations
- **Context Management**: Automatic context window management and compaction
- **Helper Functions**: Inspect context state and token usage

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` to point to your local model endpoint.

## Usage

### Basic Agent

```python
from react_agent import ReactAgent

# Create an agent
agent = ReactAgent(
    model_name="local-model",
    base_url="http://localhost:1234/v1",
    api_key="not-needed"
)

# Run a task
result = agent.run("List all Python files in the current directory")
print(result)

# Check token usage
agent.show_token_usage()

# Check context window state
agent.show_context_state()
```

### Using Subagents

```python
# Create a subagent for a specific task
subagent = agent.create_subagent(
    name="code_analyzer",
    system_prompt="You are a code analysis expert."
)

# Run task with subagent
result = subagent.run("Analyze the Python files in src/")
summary = subagent.get_summary()
```

### Custom Tools

```python
from langchain.tools import tool

@tool
def custom_calculator(expression: str) -> str:
    """Evaluate a mathematical expression."""
    return str(eval(expression))

agent.add_tool(custom_tool)
```

### MCP Server Integration

```python
# Connect to an MCP server
agent.add_mcp_server("http://localhost:8000")
```

## Architecture

The agent follows the ReAct pattern:
1. **Thought**: The agent reasons about the task
2. **Action**: The agent selects and executes a tool
3. **Observation**: The agent observes the result
4. **Repeat**: Continue until the task is complete

Context management ensures the agent stays within token limits through automatic compaction.

## License

MIT
