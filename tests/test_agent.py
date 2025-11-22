"""Tests for ReactAgent."""

import pytest
from react_agent import ReactAgent
from react_agent.context_manager import ContextManager, MessageRole
from react_agent.token_tracker import TokenTracker


class TestTokenTracker:
    """Tests for TokenTracker."""

    def test_initialization(self):
        """Test token tracker initialization."""
        tracker = TokenTracker(model_name="gpt-3.5-turbo", max_tokens=4096)
        assert tracker.max_tokens == 4096
        assert len(tracker.usage_history) == 0

    def test_count_tokens(self):
        """Test token counting."""
        tracker = TokenTracker()
        text = "Hello, world!"
        count = tracker.count_tokens(text)
        assert count > 0

    def test_record_usage(self):
        """Test recording token usage."""
        tracker = TokenTracker()
        usage = tracker.record_usage(100, 50, context="test")

        assert usage.prompt_tokens == 100
        assert usage.completion_tokens == 50
        assert usage.total_tokens == 150
        assert len(tracker.usage_history) == 1

    def test_total_usage(self):
        """Test total usage calculation."""
        tracker = TokenTracker(max_tokens=1000)
        tracker.record_usage(100, 50)
        tracker.record_usage(200, 100)

        total = tracker.get_total_usage()
        assert total["total_prompt_tokens"] == 300
        assert total["total_completion_tokens"] == 150
        assert total["total_tokens"] == 450
        assert total["tokens_remaining"] == 550

    def test_count_messages_tokens(self):
        """Test counting tokens in messages."""
        tracker = TokenTracker()
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]

        count = tracker.count_messages_tokens(messages)
        assert count > 0

    def test_is_near_limit(self):
        """Test near limit detection."""
        tracker = TokenTracker(max_tokens=1000)
        messages = [{"role": "user", "content": "test"}]

        # Should not be near limit with small message
        assert not tracker.is_near_limit(messages, threshold=0.8)


class TestContextManager:
    """Tests for ContextManager."""

    def test_initialization(self):
        """Test context manager initialization."""
        manager = ContextManager(max_tokens=4096)
        assert manager.max_tokens == 4096
        assert len(manager.messages) == 0

    def test_add_message(self):
        """Test adding messages."""
        manager = ContextManager()
        manager.add_message(MessageRole.USER, "Hello")
        manager.add_message(MessageRole.ASSISTANT, "Hi there!")

        messages = manager.get_messages()
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"

    def test_clear(self):
        """Test clearing messages."""
        manager = ContextManager()
        manager.add_message(MessageRole.USER, "Hello")
        manager.clear()

        assert len(manager.get_messages()) == 0

    def test_get_state(self):
        """Test getting context state."""
        manager = ContextManager()
        manager.add_message(MessageRole.USER, "Hello")

        state = manager.get_state()
        assert state["message_count"] == 1
        assert state["max_tokens"] == manager.max_tokens

    def test_compaction(self):
        """Test context compaction."""
        manager = ContextManager(max_tokens=1000)
        tracker = TokenTracker(max_tokens=1000)

        # Add many messages
        for i in range(20):
            manager.add_message(MessageRole.USER, f"Message {i}")
            manager.add_message(MessageRole.ASSISTANT, f"Response {i}")

        original_count = len(manager.messages)

        # Compact
        tokens_saved = manager.compact(tracker)

        new_count = len(manager.messages)
        assert new_count < original_count
        assert manager.compaction_count == 1


class TestReactAgent:
    """Tests for ReactAgent."""

    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        return ReactAgent(
            model_name="gpt-3.5-turbo",
            base_url="http://localhost:1234/v1",
            api_key="test-key"
        )

    def test_initialization(self, agent):
        """Test agent initialization."""
        assert agent.model_name == "gpt-3.5-turbo"
        assert len(agent.tools) > 0  # Should have built-in tools

    def test_builtin_tools(self, agent):
        """Test that built-in tools are available."""
        tool_names = [tool.name for tool in agent.tools]

        expected_tools = [
            "read_file",
            "write_file",
            "list_directory",
            "glob_search",
            "grep_search",
            "run_bash_command",
        ]

        for expected in expected_tools:
            assert expected in tool_names

    def test_add_tool(self, agent):
        """Test adding a custom tool."""
        from langchain.tools import tool

        @tool
        def custom_tool(input: str) -> str:
            """A custom tool."""
            return f"Processed: {input}"

        original_count = len(agent.tools)
        agent.add_tool(custom_tool)

        assert len(agent.tools) == original_count + 1

    def test_create_subagent(self, agent):
        """Test creating a subagent."""
        subagent = agent.create_subagent(
            name="test_subagent",
            system_prompt="You are a test agent"
        )

        assert subagent.name == "test_subagent"
        assert "test_subagent" in agent.subagents

    def test_get_subagent(self, agent):
        """Test retrieving a subagent."""
        agent.create_subagent(
            name="test_agent",
            system_prompt="Test"
        )

        retrieved = agent.get_subagent("test_agent")
        assert retrieved is not None
        assert retrieved.name == "test_agent"

        # Non-existent subagent
        assert agent.get_subagent("nonexistent") is None

    def test_token_usage(self, agent):
        """Test token usage tracking."""
        usage = agent.get_token_usage()

        assert "total_tokens" in usage
        assert "max_tokens" in usage
        assert usage["max_tokens"] > 0

    def test_context_state(self, agent):
        """Test context state retrieval."""
        state = agent.get_context_state()

        assert "message_count" in state
        assert "max_tokens" in state

    def test_reset(self, agent):
        """Test resetting agent."""
        # Add some context
        agent.context_manager.add_message(MessageRole.USER, "Test")

        # Reset
        agent.reset()

        # Should only have system prompt
        messages = agent.context_manager.get_messages()
        assert len(messages) == 1
        assert messages[0]["role"] == "system"


class TestTools:
    """Tests for built-in tools."""

    def test_read_file_tool(self, tmp_path):
        """Test read_file tool."""
        from react_agent.tools import read_file

        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")

        # Read file
        result = read_file.func(str(test_file))

        assert "Hello, World!" in result
        assert "test.txt" in result

    def test_write_file_tool(self, tmp_path):
        """Test write_file tool."""
        from react_agent.tools import write_file

        test_file = tmp_path / "output.txt"
        content = "Test content"

        result = write_file.func(str(test_file), content)

        assert "Wrote to file" in result
        assert test_file.read_text() == content

    def test_list_directory_tool(self, tmp_path):
        """Test list_directory tool."""
        from react_agent.tools import list_directory

        # Create test files
        (tmp_path / "file1.txt").write_text("test")
        (tmp_path / "file2.txt").write_text("test")

        result = list_directory.func(str(tmp_path))

        assert "file1.txt" in result
        assert "file2.txt" in result

    def test_glob_search_tool(self, tmp_path):
        """Test glob_search tool."""
        from react_agent.tools import glob_search

        # Create test files
        (tmp_path / "test1.py").write_text("test")
        (tmp_path / "test2.py").write_text("test")
        (tmp_path / "other.txt").write_text("test")

        result = glob_search.func("*.py", str(tmp_path))

        assert "test1.py" in result
        assert "test2.py" in result
        assert "other.txt" not in result

    def test_grep_search_tool(self, tmp_path):
        """Test grep_search tool."""
        from react_agent.tools import grep_search

        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello World\nFoo Bar\nHello Again")

        result = grep_search.func("Hello", str(test_file))

        assert "Hello World" in result
        assert "Hello Again" in result
        assert "Foo Bar" not in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
