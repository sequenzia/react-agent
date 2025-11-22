"""Advanced usage examples for ReactAgent."""

from react_agent import ReactAgent, create_simple_tool
from react_agent.utils import create_agent_from_config, AgentLogger


def example_config_based_agent():
    """Create agent from configuration file."""
    print("=" * 60)
    print("Example: Configuration-Based Agent")
    print("=" * 60)

    # Create agent from .env file
    agent = create_agent_from_config(".env")

    print("Agent created from configuration")
    print(f"Model: {agent.model_name}")

    # Use the agent
    result = agent.run("Show me the project structure")
    print("\nResult:", result)


def example_mcp_integration():
    """Example using MCP server for custom tools."""
    print("\n" + "=" * 60)
    print("Example: MCP Server Integration")
    print("=" * 60)

    agent = ReactAgent(
        model_name="local-model",
        base_url="http://localhost:1234/v1",
        api_key="not-needed"
    )

    # Add MCP server (example - would need actual MCP server running)
    print("\nAdding MCP server...")
    success = agent.add_mcp_server(
        url="http://localhost:8000",
        name="custom_tools"
    )

    if success:
        print("MCP server connected successfully")

        # List available MCP servers
        servers = agent.mcp_client.list_servers()
        print(f"\nMCP Servers: {servers}")
    else:
        print("MCP server connection failed (this is expected without a running server)")

    # Create a custom tool manually
    print("\nCreating custom tool manually...")

    def word_counter(text: str) -> str:
        """Count words in text."""
        words = text.split()
        return f"Word count: {len(words)}"

    custom_tool = create_simple_tool(
        "word_counter",
        "Count the number of words in a text string",
        word_counter
    )

    agent.add_tool(custom_tool)
    print("Custom tool added")


def example_with_logging():
    """Example using the agent logger."""
    print("\n" + "=" * 60)
    print("Example: Agent with Logging")
    print("=" * 60)

    # Create logger
    logger = AgentLogger(log_file="agent.log", verbose=True)

    logger.info("Starting agent session")

    # Create agent
    agent = ReactAgent(
        model_name="local-model",
        base_url="http://localhost:1234/v1",
        api_key="not-needed"
    )

    logger.info(f"Agent created with model: {agent.model_name}")

    # Run tasks with logging
    tasks = [
        "List Python files",
        "Check for README",
        "Find configuration files",
    ]

    for task in tasks:
        logger.info(f"Executing task: {task}")
        try:
            result = agent.run(task)
            logger.info(f"Task completed successfully")
        except Exception as e:
            logger.error(f"Task failed: {str(e)}")

    logger.info("Session completed")

    # Save logs
    logger.save_logs("agent_session.log")
    print("\nLogs saved to agent_session.log")


def example_context_compaction():
    """Example demonstrating context compaction."""
    print("\n" + "=" * 60)
    print("Example: Context Compaction")
    print("=" * 60)

    # Create agent with small context window
    agent = ReactAgent(
        model_name="local-model",
        base_url="http://localhost:1234/v1",
        api_key="not-needed",
        max_tokens=1024  # Small context to trigger compaction
    )

    print("Initial context state:")
    agent.show_context_state()

    # Run many tasks to fill context
    print("\nRunning multiple tasks to fill context...")
    for i in range(10):
        agent.run(f"Task {i + 1}: List files in directory")

        if i % 3 == 0:
            print(f"\nAfter task {i + 1}:")
            state = agent.get_context_state()
            print(f"  Messages: {state['message_count']}")
            print(f"  Compactions: {state['compaction_count']}")

    print("\nFinal context state:")
    agent.show_context_state()


def example_token_tracking():
    """Example focused on token tracking features."""
    print("\n" + "=" * 60)
    print("Example: Token Tracking")
    print("=" * 60)

    agent = ReactAgent(
        model_name="local-model",
        base_url="http://localhost:1234/v1",
        api_key="not-needed"
    )

    # Run some tasks
    tasks = [
        "List all files",
        "Find Python files",
        "Show directory structure",
    ]

    print("Running tasks and tracking tokens...\n")

    for i, task in enumerate(tasks, 1):
        print(f"Task {i}: {task}")
        agent.run(task)

        # Show usage after each task
        usage = agent.get_token_usage()
        print(f"  Tokens used: {usage['total_tokens']}")
        print(f"  Tokens remaining: {usage['tokens_remaining']}")
        print()

    # Final summary
    print("=" * 60)
    print("Final Token Usage:")
    print("=" * 60)
    agent.show_token_usage()


def example_state_persistence():
    """Example showing state export and import."""
    print("\n" + "=" * 60)
    print("Example: State Persistence")
    print("=" * 60)

    # Create and use agent
    print("Creating agent and running tasks...")
    agent = ReactAgent(
        model_name="local-model",
        base_url="http://localhost:1234/v1",
        api_key="not-needed"
    )

    agent.run("List all Python files")
    agent.run("Find configuration files")

    # Create subagent
    subagent = agent.create_subagent(
        "analyzer",
        "You analyze code files"
    )
    subagent.run("Analyze project structure")

    # Export state
    print("\nExporting agent state...")
    agent.export_state("full_agent_state.json")

    # Export subagent state
    print("Exporting subagent state...")
    subagent.export_state("subagent_state.json")

    print("\nState files created:")
    print("  - full_agent_state.json")
    print("  - full_agent_state_context.json")
    print("  - subagent_state.json")

    # Show what was saved
    import json
    with open("full_agent_state.json", 'r') as f:
        state = json.load(f)

    print("\nAgent state summary:")
    print(f"  Model: {state['model_name']}")
    print(f"  Total tokens: {state['token_usage']['total_tokens']}")
    print(f"  Messages: {state['context_state']['message_count']}")
    print(f"  Subagents: {', '.join(state['subagents'])}")


def example_complete_workflow():
    """Example showing a complete real-world workflow."""
    print("\n" + "=" * 60)
    print("Example: Complete Workflow")
    print("=" * 60)

    # Initialize
    logger = AgentLogger(verbose=True)
    logger.info("Starting complete workflow example")

    # Create agent
    agent = ReactAgent(
        model_name="local-model",
        base_url="http://localhost:1234/v1",
        api_key="not-needed"
    )

    # Phase 1: Research
    print("\n--- Phase 1: Research ---")
    researcher = agent.create_subagent(
        "researcher",
        "You gather information about code projects"
    )
    research = researcher.run("Analyze the project structure and list all components")
    logger.info("Research phase completed")

    # Phase 2: Analysis
    print("\n--- Phase 2: Analysis ---")
    analyzer = agent.create_subagent(
        "analyzer",
        "You analyze code and provide insights"
    )
    analysis = analyzer.run(f"Analyze this project info: {research.summary}")
    logger.info("Analysis phase completed")

    # Phase 3: Documentation
    print("\n--- Phase 3: Documentation ---")
    documenter = agent.create_subagent(
        "documenter",
        "You create technical documentation"
    )
    docs = documenter.run(f"Create documentation from: {analysis.summary}")
    logger.info("Documentation phase completed")

    # Final report
    print("\n" + "=" * 60)
    print("Workflow Complete!")
    print("=" * 60)

    print(f"\nResearch tokens: {research.token_usage['total_tokens']}")
    print(f"Analysis tokens: {analysis.token_usage['total_tokens']}")
    print(f"Documentation tokens: {docs.token_usage['total_tokens']}")

    total_time = research.execution_time + analysis.execution_time + docs.execution_time
    print(f"\nTotal execution time: {total_time:.2f}s")

    # Save everything
    agent.export_state("workflow_state.json")
    logger.save_logs("workflow.log")

    print("\nFiles saved:")
    print("  - workflow_state.json")
    print("  - workflow.log")


if __name__ == "__main__":
    print("ReactAgent Advanced Examples")
    print("=" * 60)
    print("\nThese examples demonstrate advanced features:")
    print("1. Configuration-based setup")
    print("2. MCP server integration")
    print("3. Logging and monitoring")
    print("4. Context compaction")
    print("5. Token tracking")
    print("6. State persistence")
    print("7. Complete workflows")
    print("\nNote: Requires a local model server running")
    print("\nExamples ready to run!")

    # Uncomment to run:
    # example_config_based_agent()
    # example_mcp_integration()
    # example_with_logging()
    # example_context_compaction()
    # example_token_tracking()
    # example_state_persistence()
    # example_complete_workflow()
