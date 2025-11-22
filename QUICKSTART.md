# ReactAgent Quick Start Guide

Get started with ReactAgent in minutes!

## Installation

This project uses [UV](https://docs.astral.sh/uv/) for fast, reliable Python package management.

1. **Install UV:**

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

2. **Install dependencies:**

```bash
# Install all dependencies
uv sync

# Install with development dependencies
uv sync --all-extras
```

3. **Set up configuration:**

```bash
cp .env.example .env
```

Edit `.env` to configure your local model endpoint:

```bash
OPENAI_API_BASE=http://localhost:1234/v1
OPENAI_API_KEY=not-needed
MODEL_NAME=local-model
```

## Set Up Local Model (Optional)

If you don't have a local model server, you can use:

### Option 1: LM Studio

1. Download [LM Studio](https://lmstudio.ai/)
2. Download a model (e.g., Mistral, Llama)
3. Start the local server (default: http://localhost:1234/v1)

### Option 2: Ollama

1. Install [Ollama](https://ollama.ai/)
2. Pull a model: `ollama pull mistral`
3. The API is at http://localhost:11434/v1

### Option 3: Use OpenAI API

Set your OpenAI API key in `.env`:

```bash
OPENAI_API_KEY=sk-your-api-key
# Remove or comment out OPENAI_API_BASE
```

## Basic Usage

### 1. Create Your First Agent

```python
from react_agent import ReactAgent

# Create agent
agent = ReactAgent(
    model_name="local-model",
    base_url="http://localhost:1234/v1",
    api_key="not-needed"
)

# Run a task
result = agent.run("List all Python files in the current directory")
print(result)
```

### 2. Use Built-in Tools

The agent comes with tools for:

```python
# File operations
agent.run("Read the README.md file")
agent.run("Write 'Hello World' to output.txt")

# File search
agent.run("Find all Python files in the project")
agent.run("Search for 'TODO' in all Python files")

# Bash commands
agent.run("Run 'git status' and tell me what changed")
```

### 3. Monitor Token Usage

```python
# After running tasks
agent.show_token_usage()

# Get usage programmatically
usage = agent.get_token_usage()
print(f"Total tokens: {usage['total_tokens']}")
```

### 4. Check Context State

```python
# Show context window state
agent.show_context_state()

# Get state programmatically
state = agent.get_context_state()
print(f"Messages: {state['message_count']}")
```

### 5. Create a Subagent

```python
# Create specialized subagent
code_analyzer = agent.create_subagent(
    name="code_analyzer",
    system_prompt="You are a code analysis expert."
)

# Use the subagent
result = code_analyzer.run("Analyze the Python files")

# Get summary for main agent
print(result.summary)
```

### 6. Add Custom Tools

```python
from langchain.tools import tool

@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression."""
    return str(eval(expression))

agent.add_tool(calculator)

# Now the agent can use your custom tool
result = agent.run("Calculate 25 * 4 + 10")
```

## Configuration from File

Create an agent from your `.env` configuration:

```python
from react_agent.utils import create_agent_from_config

agent = create_agent_from_config(".env")
result = agent.run("Your task here")
```

## Examples

Check out the `examples/` directory for more:

- `basic_usage.py` - Basic features and built-in tools
- `subagent_usage.py` - Working with subagents
- `advanced_usage.py` - Advanced features and workflows

Run an example:

```bash
# With UV
uv run python examples/basic_usage.py

# Or activate the virtual environment first
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python examples/basic_usage.py
```

## Testing

Run the test suite:

```bash
# With UV
uv run pytest tests/

# Or activate the virtual environment first
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pytest tests/
```

## Common Patterns

### Pattern 1: Research and Analysis

```python
# Create specialized agents
researcher = agent.create_subagent(
    "researcher",
    "You gather and organize information"
)

analyzer = agent.create_subagent(
    "analyzer",
    "You analyze data and provide insights"
)

# Execute workflow
data = researcher.run("Find all Python files and their sizes")
insights = analyzer.run(f"Analyze this data: {data.summary}")
```

### Pattern 2: Context Management

```python
# Agent automatically manages context
for i in range(100):
    agent.run(f"Task {i}")

# View compaction statistics
state = agent.get_context_state()
print(f"Compactions: {state['compaction_count']}")
```

### Pattern 3: State Persistence

```python
# Save agent state
agent.export_state("my_agent_state.json")

# Later: load and inspect
import json
with open("my_agent_state.json") as f:
    state = json.load(f)
    print(state["token_usage"])
```

## Troubleshooting

### Model Connection Issues

```python
# Test your model connection
import requests
response = requests.get("http://localhost:1234/v1/models")
print(response.json())
```

### Token Limit Errors

```python
# Reduce max_tokens or enable more aggressive compaction
agent = ReactAgent(
    max_tokens=2048,  # Smaller context
)
```

### Debugging

```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use the agent logger
from react_agent.utils import AgentLogger
logger = AgentLogger(log_file="debug.log")
```

## Next Steps

1. **Explore Examples**: Check `examples/` for comprehensive examples
2. **Read the API**: Review module docstrings for detailed API docs
3. **Create Custom Tools**: Build domain-specific tools for your use case
4. **Integrate MCP Servers**: Connect to MCP servers for extended functionality
5. **Build Workflows**: Chain multiple subagents for complex tasks

## Getting Help

- Check the [README.md](README.md) for feature overview
- Review the [examples/](examples/) directory
- Read the source code docstrings
- Open an issue on GitHub

## Quick Reference

```python
# Create agent
agent = ReactAgent(model_name="...", base_url="...")

# Run task
result = agent.run("Your task")

# Create subagent
sub = agent.create_subagent("name", "prompt")

# Add custom tool
agent.add_tool(my_tool)

# Monitor usage
agent.show_token_usage()
agent.show_context_state()

# Save state
agent.export_state("state.json")

# Reset
agent.reset()
```

Happy coding! 🚀
