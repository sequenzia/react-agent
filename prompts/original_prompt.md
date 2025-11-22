Create a general AI Agent in Python. Follow these requirements:

- It must follow the ReAct (Reasoning and Acting) Pattern
- It must use LangChain, LangGraph and LangSmith
- It must work with locally hosted models based on OpenAI's APIs
- It must have built in tools for
  - Reading and writing to the filesystem
  - Run Glob
  - Run Grep searches
  - Run Bash commands
- It must work with custom tools including MCP servers
- It must be able to create and work with subagents
  - Subagents should maintain their own internal state of the context window
  - Subagents should return a summary of their context back to the main agent
- It must track token usage
- It must have have functionality that manages the state of the context window including context compaction
- It must have helper functions that
  - Shows current state of the context window
  - Shows current token usage
