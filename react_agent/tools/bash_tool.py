"""Bash command execution tool."""

import subprocess
import shlex
from typing import Optional
from langchain.tools import tool


@tool
def run_bash_command(
    command: str,
    timeout: int = 30,
    working_dir: Optional[str] = None,
    capture_output: bool = True
) -> str:
    """Execute a bash command and return the output.

    Args:
        command: Bash command to execute
        timeout: Maximum execution time in seconds (default: 30)
        working_dir: Working directory for command execution (default: current)
        capture_output: Whether to capture and return output (default: True)

    Returns:
        Command output or error message

    Examples:
        run_bash_command("ls -la")
        run_bash_command("python script.py", timeout=60)
        run_bash_command("npm install", working_dir="/path/to/project")

    Security Warning:
        This tool executes arbitrary commands. Use with caution and
        validate inputs in production environments.
    """
    try:
        # Parse command safely
        # Note: In production, you should implement more robust command validation
        if not command.strip():
            return "Error: Empty command"

        # Execute command
        result = subprocess.run(
            command,
            shell=True,
            capture_output=capture_output,
            text=True,
            timeout=timeout,
            cwd=working_dir
        )

        # Format output
        output = f"Command: {command}\n"

        if working_dir:
            output += f"Working Directory: {working_dir}\n"

        output += f"Exit Code: {result.returncode}\n\n"

        if result.stdout:
            output += "STDOUT:\n"
            output += result.stdout

        if result.stderr:
            output += "\nSTDERR:\n"
            output += result.stderr

        if result.returncode != 0:
            output += f"\n\nWarning: Command exited with non-zero status: {result.returncode}"

        return output

    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout} seconds"
    except FileNotFoundError:
        return f"Error: Command not found or invalid: {command}"
    except PermissionError:
        return f"Error: Permission denied executing command: {command}"
    except Exception as e:
        return f"Error executing command: {str(e)}"
