"""MCP (Model Context Protocol) server integration for custom tools."""

from typing import List, Dict, Any, Optional
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
import json
import asyncio
import logging

logger = logging.getLogger(__name__)


class MCPServerConfig(BaseModel):
    """Configuration for an MCP server."""

    url: str = Field(..., description="URL of the MCP server")
    name: str = Field(..., description="Name of the MCP server")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    timeout: int = Field(30, description="Request timeout in seconds")


class MCPClient:
    """Client for connecting to MCP servers and using their tools."""

    def __init__(self):
        """Initialize the MCP client."""
        self.servers: Dict[str, MCPServerConfig] = {}
        self.tools: Dict[str, StructuredTool] = {}

    def add_server(
        self,
        url: str,
        name: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 30
    ) -> bool:
        """Add an MCP server.

        Args:
            url: URL of the MCP server
            name: Name for the server (default: derived from URL)
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds

        Returns:
            True if server was added successfully
        """
        if name is None:
            # Extract name from URL
            name = url.split("//")[-1].split("/")[0].replace(".", "_")

        config = MCPServerConfig(
            url=url,
            name=name,
            api_key=api_key,
            timeout=timeout
        )

        self.servers[name] = config

        # Discover and register tools from this server
        try:
            self._discover_tools(name)
            logger.info(f"Successfully connected to MCP server: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MCP server {name}: {str(e)}")
            return False

    def _discover_tools(self, server_name: str):
        """Discover available tools from an MCP server.

        Args:
            server_name: Name of the server to discover tools from
        """
        # This is a placeholder implementation
        # In a real implementation, you would:
        # 1. Connect to the MCP server
        # 2. Query available tools
        # 3. Parse tool schemas
        # 4. Create LangChain StructuredTool instances
        # 5. Register them in self.tools

        # Example structure:
        config = self.servers[server_name]

        # Mock discovery (replace with actual MCP protocol)
        logger.info(f"Discovering tools from {config.url}")

        # For now, log that discovery would happen here
        logger.warning(
            f"MCP tool discovery for {server_name} is not yet implemented. "
            "This is a placeholder for MCP integration."
        )

    def get_tools(self) -> List[StructuredTool]:
        """Get all registered tools from MCP servers.

        Returns:
            List of LangChain tools
        """
        return list(self.tools.values())

    def remove_server(self, name: str) -> bool:
        """Remove an MCP server and its tools.

        Args:
            name: Name of the server to remove

        Returns:
            True if server was removed successfully
        """
        if name not in self.servers:
            logger.warning(f"Server {name} not found")
            return False

        # Remove tools from this server
        tools_to_remove = [
            tool_name for tool_name, tool in self.tools.items()
            if tool_name.startswith(f"{name}_")
        ]

        for tool_name in tools_to_remove:
            del self.tools[tool_name]

        # Remove server
        del self.servers[name]

        logger.info(f"Removed MCP server: {name}")
        return True

    def list_servers(self) -> List[Dict[str, Any]]:
        """List all registered MCP servers.

        Returns:
            List of server information dictionaries
        """
        return [
            {
                "name": name,
                "url": config.url,
                "tool_count": len([t for t in self.tools if t.startswith(f"{name}_")])
            }
            for name, config in self.servers.items()
        ]

    def create_custom_tool(
        self,
        name: str,
        description: str,
        func: callable,
        args_schema: Optional[type[BaseModel]] = None
    ) -> StructuredTool:
        """Create a custom tool manually (without MCP server).

        Args:
            name: Name of the tool
            description: Description of what the tool does
            func: The function to execute
            args_schema: Optional Pydantic model for arguments

        Returns:
            LangChain StructuredTool
        """
        tool = StructuredTool.from_function(
            func=func,
            name=name,
            description=description,
            args_schema=args_schema
        )

        self.tools[name] = tool
        logger.info(f"Created custom tool: {name}")

        return tool


# Example custom tool creation helper
def create_simple_tool(name: str, description: str, func: callable) -> StructuredTool:
    """Helper function to create a simple custom tool.

    Args:
        name: Name of the tool
        description: Description of the tool
        func: Function to execute

    Returns:
        LangChain StructuredTool

    Example:
        def my_tool(query: str) -> str:
            return f"Processing: {query}"

        tool = create_simple_tool(
            "my_custom_tool",
            "Does something useful",
            my_tool
        )
    """
    return StructuredTool.from_function(
        func=func,
        name=name,
        description=description
    )
