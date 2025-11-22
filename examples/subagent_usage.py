"""Example demonstrating subagent usage."""

from react_agent import ReactAgent


def example_basic_subagent():
    """Create and use a basic subagent."""
    print("=" * 60)
    print("Example: Basic Subagent Usage")
    print("=" * 60)

    # Create main agent
    agent = ReactAgent(
        model_name="local-model",
        base_url="http://localhost:1234/v1",
        api_key="not-needed"
    )

    # Create a specialized subagent for code analysis
    code_analyzer = agent.create_subagent(
        name="code_analyzer",
        system_prompt="""You are a specialized code analysis agent.
Your role is to analyze code files and provide insights about:
- Code quality
- Potential bugs
- Best practices
- Optimization opportunities

Always provide detailed, actionable feedback."""
    )

    # Use the subagent
    print("\nRunning subagent task...")
    result = code_analyzer.run("Analyze the Python files in the react_agent directory")

    print(f"\nSubagent completed: {result.success}")
    print(f"Execution time: {result.execution_time:.2f}s")
    print(f"Tokens used: {result.token_usage['total_tokens']}")

    # Get summary for parent agent
    print("\n" + "=" * 60)
    print("Subagent Summary:")
    print("=" * 60)
    print(result.summary)


def example_multiple_subagents():
    """Example using multiple specialized subagents."""
    print("\n" + "=" * 60)
    print("Example: Multiple Specialized Subagents")
    print("=" * 60)

    # Create main agent
    agent = ReactAgent(
        model_name="local-model",
        base_url="http://localhost:1234/v1",
        api_key="not-needed"
    )

    # Create specialized subagents
    subagents = {
        "file_manager": agent.create_subagent(
            name="file_manager",
            system_prompt="You are a file management specialist. "
                         "Handle file operations efficiently and safely."
        ),
        "data_analyzer": agent.create_subagent(
            name="data_analyzer",
            system_prompt="You are a data analysis expert. "
                         "Extract insights from data and provide statistical summaries."
        ),
        "documentation_writer": agent.create_subagent(
            name="documentation_writer",
            system_prompt="You are a technical documentation expert. "
                         "Write clear, comprehensive documentation."
        ),
    }

    # Use different subagents for different tasks
    print("\n1. File Manager: Organizing project files")
    file_result = subagents["file_manager"].run(
        "List all Python files and organize them by subdirectory"
    )

    print("\n2. Data Analyzer: Analyzing code statistics")
    data_result = subagents["data_analyzer"].run(
        "Analyze the size and line count statistics of Python files"
    )

    print("\n3. Documentation Writer: Creating README")
    doc_result = subagents["documentation_writer"].run(
        "Review the project structure and suggest improvements to README.md"
    )

    # Show summary of all subagents
    print("\n" + "=" * 60)
    print("Subagent Summaries:")
    print("=" * 60)

    for name, subagent in subagents.items():
        print(f"\n{name.upper()}:")
        print(subagent.get_summary())


def example_subagent_context_management():
    """Example showing subagent independent context management."""
    print("\n" + "=" * 60)
    print("Example: Subagent Context Management")
    print("=" * 60)

    # Create main agent
    agent = ReactAgent(
        model_name="local-model",
        base_url="http://localhost:1234/v1",
        api_key="not-needed"
    )

    # Create subagent with smaller context window
    subagent = agent.create_subagent(
        name="test_agent",
        system_prompt="You are a test agent for demonstrating context management.",
        max_tokens=1024  # Smaller context
    )

    # Run multiple tasks with the subagent
    tasks = [
        "Task 1: List files",
        "Task 2: Analyze directory structure",
        "Task 3: Find Python files",
        "Task 4: Search for configuration files",
        "Task 5: Provide summary",
    ]

    for task in tasks:
        print(f"\nExecuting: {task}")
        result = subagent.run(task)

        # Show context state after each task
        context_state = subagent.get_context_state()
        print(f"Context: {context_state['message_count']} messages, "
              f"{context_state['compaction_count']} compactions")

    # Final summary
    print("\n" + "=" * 60)
    print("Final Subagent State:")
    print("=" * 60)
    print(subagent.get_summary())


def example_subagent_delegation():
    """Example of main agent delegating work to subagents."""
    print("\n" + "=" * 60)
    print("Example: Task Delegation Pattern")
    print("=" * 60)

    # Create main orchestrator agent
    agent = ReactAgent(
        model_name="local-model",
        base_url="http://localhost:1234/v1",
        api_key="not-needed"
    )

    # Create specialized subagents
    researcher = agent.create_subagent(
        name="researcher",
        system_prompt="You research and gather information from files."
    )

    analyzer = agent.create_subagent(
        name="analyzer",
        system_prompt="You analyze information and draw conclusions."
    )

    reporter = agent.create_subagent(
        name="reporter",
        system_prompt="You create comprehensive reports from analyzed data."
    )

    # Simulate a multi-step workflow
    print("\nStep 1: Research phase")
    research_result = researcher.run(
        "Find all Python files and list their purposes"
    )

    print("\nStep 2: Analysis phase")
    analysis_result = analyzer.run(
        f"Analyze this research data: {research_result.result}"
    )

    print("\nStep 3: Reporting phase")
    report_result = reporter.run(
        f"Create a summary report from this analysis: {analysis_result.result}"
    )

    # Show final report
    print("\n" + "=" * 60)
    print("Final Report:")
    print("=" * 60)
    print(report_result.result)

    # Show token usage across all subagents
    print("\n" + "=" * 60)
    print("Token Usage by Subagent:")
    print("=" * 60)
    for name in ["researcher", "analyzer", "reporter"]:
        subagent = agent.get_subagent(name)
        usage = subagent.get_token_usage()
        print(f"{name}: {usage['total_tokens']} tokens")


if __name__ == "__main__":
    print("ReactAgent Subagent Examples")
    print("=" * 60)
    print("\nThese examples demonstrate the subagent system:")
    print("1. Basic subagent creation and usage")
    print("2. Multiple specialized subagents")
    print("3. Independent context management")
    print("4. Task delegation patterns")
    print("\nNote: Requires a local model server running")
    print("\nExamples ready to run!")
    print("Uncomment the function calls to execute.")

    # Uncomment to run:
    # example_basic_subagent()
    # example_multiple_subagents()
    # example_subagent_context_management()
    # example_subagent_delegation()
