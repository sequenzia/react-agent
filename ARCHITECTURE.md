# ReactAgent Architecture

This document describes the architecture and design of the ReactAgent system.

## Overview

ReactAgent is a general-purpose AI agent built on the ReAct (Reasoning and Acting) pattern, combining modern AI frameworks with robust context management and extensibility.

## Core Components

### 1. ReactAgent (`agent.py`)

The main agent class that orchestrates all functionality.

**Key Features:**
- ReAct pattern implementation using LangChain
- Tool management and execution
- Context and token tracking integration
- Subagent creation and management
- State persistence

**Dependencies:**
- LangChain for LLM integration
- LangGraph for workflow management (future)
- LangSmith for observability (optional)

### 2. TokenTracker (`token_tracker.py`)

Manages token counting and usage tracking.

**Features:**
- Accurate token counting using tiktoken
- Usage history tracking
- Near-limit detection
- Usage statistics and reporting

**Key Methods:**
- `count_tokens()` - Count tokens in text
- `count_messages_tokens()` - Count tokens in message list
- `record_usage()` - Record an interaction
- `get_total_usage()` - Get cumulative statistics
- `is_near_limit()` - Check if approaching limit

### 3. ContextManager (`context_manager.py`)

Handles conversation context and performs compaction.

**Features:**
- Message history management
- Automatic context compaction
- Configurable compaction strategies
- Context export/import

**Compaction Strategy:**
- Keep first N messages (system prompt, initial context)
- Keep last N messages (recent context)
- Summarize middle messages

**Key Methods:**
- `add_message()` - Add message to context
- `get_messages()` - Retrieve all messages
- `compact()` - Perform context compaction
- `get_state()` - Get context statistics

### 4. Subagent (`subagent.py`)

Specialized agents with independent context for task delegation.

**Features:**
- Independent context window
- Separate token tracking
- Summary generation for parent agent
- ReAct loop execution

**Use Cases:**
- Task delegation
- Specialized expertise
- Parallel processing
- Context isolation

**Key Methods:**
- `run()` - Execute task using ReAct
- `get_summary()` - Generate summary for parent
- `get_context_state()` - Get context statistics
- `reset()` - Clear context

### 5. MCPClient (`mcp_client.py`)

Integration layer for Model Context Protocol servers.

**Features:**
- MCP server connection management
- Tool discovery and registration
- Custom tool creation
- Server lifecycle management

**Key Methods:**
- `add_server()` - Connect to MCP server
- `get_tools()` - Get all registered tools
- `remove_server()` - Disconnect from server
- `create_custom_tool()` - Create manual tool

### 6. Built-in Tools (`tools/`)

Comprehensive set of filesystem and system tools.

**Tools Provided:**
- `read_file` - Read file contents
- `write_file` - Write to files
- `list_directory` - List directory contents
- `glob_search` - Pattern-based file search
- `grep_search` - Text search in files
- `run_bash_command` - Execute shell commands

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        ReactAgent                           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              LangChain Agent Executor                 │  │
│  │          (ReAct Pattern Implementation)               │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Context    │  │    Token     │  │     MCP      │     │
│  │   Manager    │  │   Tracker    │  │    Client    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                   Built-in Tools                      │  │
│  │  [File] [Glob] [Grep] [Bash] [Custom] [MCP]         │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                     Subagents                         │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐              │  │
│  │  │SubAgent1│  │SubAgent2│  │SubAgent3│  ...         │  │
│  │  └─────────┘  └─────────┘  └─────────┘              │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │   Local Model Server   │
              │  (OpenAI-compatible)   │
              └───────────────────────┘
```

## Data Flow

### 1. Basic Task Execution

```
User Task → ReactAgent
    ↓
Add to Context (ContextManager)
    ↓
Check Token Limit (TokenTracker)
    ↓
Compact if needed (ContextManager)
    ↓
Create Agent Executor (LangChain)
    ↓
Execute ReAct Loop:
    - Thought (LLM reasoning)
    - Action (Tool selection)
    - Observation (Tool result)
    - Repeat until done
    ↓
Record Token Usage (TokenTracker)
    ↓
Return Result
```

### 2. Subagent Delegation

```
User Task → ReactAgent
    ↓
Identify subtask
    ↓
Create/Get Subagent
    ↓
Delegate to Subagent:
    - Independent context
    - Independent tokens
    - ReAct execution
    ↓
Get Summary from Subagent
    ↓
Integrate Summary into Main Context
    ↓
Continue Main Task
```

### 3. Context Compaction

```
New Message Added
    ↓
Check Token Count (TokenTracker)
    ↓
Near Limit? (> 70% of max)
    ↓
Trigger Compaction:
    - Keep first N (system prompt)
    - Keep last N (recent context)
    - Summarize middle
    ↓
Replace Messages
    ↓
Update Token Count
```

## Design Patterns

### 1. ReAct Pattern

The core reasoning loop:

```python
while not done:
    thought = llm.think(context)
    action = llm.select_action(thought, tools)
    observation = execute_tool(action)
    context.add(thought, action, observation)
    done = has_final_answer(observation)
```

### 2. Strategy Pattern

Context compaction uses configurable strategies:

```python
CompactionStrategy(
    keep_first_n=2,    # System prompt + initial
    keep_last_n=10,    # Recent context
    summarize_middle=True  # Compress middle
)
```

### 3. Factory Pattern

Tool creation and registration:

```python
# Built-in tools
tools = _initialize_builtin_tools()

# Custom tools
custom = create_simple_tool(name, desc, func)

# MCP tools
mcp_tools = mcp_client.get_tools()
```

### 4. Observer Pattern

Token tracking observes all interactions:

```python
# Every interaction recorded
tracker.record_usage(
    prompt_tokens,
    completion_tokens,
    context
)
```

## Extension Points

### 1. Custom Tools

Add domain-specific functionality:

```python
@tool
def my_custom_tool(input: str) -> str:
    """Tool description."""
    return process(input)

agent.add_tool(my_custom_tool)
```

### 2. MCP Servers

Connect to external tool providers:

```python
agent.add_mcp_server("http://localhost:8000")
```

### 3. Compaction Strategies

Customize context management:

```python
custom_strategy = CompactionStrategy(
    keep_first_n=5,
    keep_last_n=20,
    summarize_middle=True
)

context_manager = ContextManager(
    compaction_strategy=custom_strategy
)
```

### 4. Subagent Specialization

Create domain experts:

```python
expert = agent.create_subagent(
    "domain_expert",
    "You are an expert in X. Always Y."
)
```

## Performance Considerations

### Token Usage

- Automatic tracking prevents cost overruns
- Context compaction prevents limit errors
- Subagents isolate token usage

### Context Window

- Configurable max tokens
- Automatic compaction at threshold
- Summary-based compression

### Caching

- TokenTracker caches token counts
- Message encoding reused
- Tool instances cached

## Security Considerations

### Bash Tool

- Shell=True poses injection risk
- Production: implement command whitelist
- Validate all inputs
- Use timeout limits

### File Operations

- Path validation required
- Permission checking
- Sandboxing recommended

### API Keys

- Never commit keys
- Use environment variables
- Rotate regularly

## Future Enhancements

1. **LangGraph Integration**
   - Complex workflow management
   - Conditional branching
   - Parallel execution

2. **Advanced Context Management**
   - Semantic compression
   - Vector-based retrieval
   - Long-term memory

3. **MCP Protocol**
   - Full MCP implementation
   - Dynamic tool loading
   - Server discovery

4. **Observability**
   - LangSmith integration
   - Detailed tracing
   - Performance metrics

5. **Multi-modal Support**
   - Image understanding
   - Document processing
   - Audio/video tools

## Testing Strategy

### Unit Tests

- Component isolation
- Mock external dependencies
- Test edge cases

### Integration Tests

- End-to-end workflows
- Tool execution
- Context management

### Performance Tests

- Token counting accuracy
- Compaction effectiveness
- Response latency

## Conclusion

The ReactAgent architecture provides a robust, extensible foundation for building AI agents with:

- Proven ReAct pattern
- Comprehensive tool ecosystem
- Intelligent context management
- Task delegation capabilities
- Production-ready features

The modular design allows easy customization while maintaining reliability and performance.
