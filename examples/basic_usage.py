"""Basic usage example for ReactAgent."""

import os
from react_agent import ReactAgent

# Example 1: Basic agent with local model
def example_basic_agent():
    """Create a basic agent and run a simple task."""
    print("=" * 60)
    print("Example 1: Basic Agent Usage")
    print("=" * 60)

    # Create agent pointing to local model
    agent = ReactAgent(
        model_name="local-model",
        base_url="http://localhost:1234/v1",
        api_key="not-needed",
        max_tokens=4096
    )

    # Run a simple task
    result = agent.run("List all Python files in the current directory")
    print("\nResult:", result)

    # Show token usage
    print("\n" + "=" * 60)
    agent.show_token_usage()

    # Show context state
    print("\n" + "=" * 60)
    agent.show_context_state()


# Example 2: Using specific tools
def example_using_tools():
    """Example using specific built-in tools."""
    print("\n" + "=" * 60)
    print("Example 2: Using Built-in Tools")
    print("=" * 60)

    agent = ReactAgent(
        model_name="local-model",
        base_url="http://localhost:1234/v1",
        api_key="not-needed"
    )

    # Task that requires multiple tools
    task = """
    1. Search for all markdown files in the current directory
    2. Read the README.md file
    3. Count how many lines it has
    """

    result = agent.run(task)
    print("\nResult:", result)


# Example 3: Context management
def example_context_management():
    """Example showing context window management."""
    print("\n" + "=" * 60)
    print("Example 3: Context Window Management")
    print("=" * 60)

    agent = ReactAgent(
        model_name="local-model",
        base_url="http://localhost:1234/v1",
        api_key="not-needed",
        max_tokens=2048  # Smaller context for demonstration
    )

    # Run multiple tasks to fill context
    tasks = [
        "What files are in the current directory?",
        "What is in the README.md file?",
        "Search for Python files",
        "What configuration files exist?",
    ]

    for i, task in enumerate(tasks, 1):
        print(f"\nTask {i}: {task}")
        result = agent.run(task)
        print(f"Result: {result[:100]}...")  # Truncate for display

    # Show final context state
    print("\n" + "=" * 60)
    print("Final Context State:")
    agent.show_context_state()


# Example 4: Custom tools
def example_custom_tools():
    """Example adding custom tools to the agent."""
    print("\n" + "=" * 60)
    print("Example 4: Custom Tools")
    print("=" * 60)

    from langchain.tools import tool

    # Define a custom tool
    @tool
    def calculate_fibonacci(n: int) -> str:
        """Calculate the nth Fibonacci number.

        Args:
            n: The position in the Fibonacci sequence
        """
        if n <= 0:
            return "Please provide a positive integer"
        elif n == 1 or n == 2:
            return "1"

        a, b = 1, 1
        for _ in range(n - 2):
            a, b = b, a + b

        return str(b)

    # Create agent and add custom tool
    agent = ReactAgent(
        model_name="local-model",
        base_url="http://localhost:1234/v1",
        api_key="not-needed"
    )

    agent.add_tool(calculate_fibonacci)

    # Use the custom tool
    result = agent.run("Calculate the 10th Fibonacci number")
    print("\nResult:", result)


# Example 5: Exporting state
def example_export_state():
    """Example exporting agent state."""
    print("\n" + "=" * 60)
    print("Example 5: Exporting Agent State")
    print("=" * 60)

    agent = ReactAgent(
        model_name="local-model",
        base_url="http://localhost:1234/v1",
        api_key="not-needed"
    )

    # Run some tasks
    agent.run("List files in current directory")
    agent.run("What Python files are present?")

    # Export state
    agent.export_state("agent_state.json")
    print("\nAgent state exported to agent_state.json")

    # Show stats
    stats = agent.get_token_usage()
    print(f"\nTotal tokens used: {stats['total_tokens']}")
    print(f"Interactions: {stats['interaction_count']}")


if __name__ == "__main__":
    # Note: These examples require a local model server running
    # You can use LM Studio, Ollama, or similar tools
    # Set the correct base_url for your setup

    print("ReactAgent Examples")
    print("=" * 60)
    print("\nNote: Make sure you have a local model server running")
    print("Example: LM Studio at http://localhost:1234/v1")
    print("\nSkip examples requiring model execution? (y/n): ", end="")

    # For demonstration, we'll just show the structure
    # Uncomment to actually run:
    # example_basic_agent()
    # example_using_tools()
    # example_context_management()
    # example_custom_tools()
    # example_export_state()

    print("\nExamples ready to run!")
    print("Uncomment the function calls at the bottom of this file to execute.")
