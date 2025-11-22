"""Glob pattern matching tool."""

from pathlib import Path
from typing import Optional
from langchain.tools import tool


@tool
def glob_search(pattern: str, root_path: str = ".", recursive: bool = True) -> str:
    """Search for files matching a glob pattern.

    Args:
        pattern: Glob pattern to match (e.g., "*.py", "**/*.txt")
        root_path: Root directory to search from (default: current directory)
        recursive: Use recursive search with ** (default: True)

    Returns:
        List of matching file paths

    Examples:
        glob_search("*.py")
        glob_search("**/*.txt", root_path="/home/user")
        glob_search("test_*.py", root_path="tests")
    """
    try:
        root = Path(root_path).expanduser().resolve()

        if not root.exists():
            return f"Error: Root path not found: {root_path}"

        if not root.is_dir():
            return f"Error: Root path is not a directory: {root_path}"

        # Use rglob for recursive patterns or glob for non-recursive
        if recursive and "**" in pattern:
            matches = list(root.glob(pattern))
        elif recursive:
            matches = list(root.rglob(pattern))
        else:
            matches = list(root.glob(pattern))

        if not matches:
            return f"No files found matching pattern: {pattern}"

        # Sort matches and convert to relative paths
        matches.sort()
        relative_matches = [str(m.relative_to(root)) for m in matches]

        # Separate files and directories
        files = [m for m in matches if m.is_file()]
        dirs = [m for m in matches if m.is_dir()]

        result = f"Glob search: {pattern}\n" \
                f"Root: {root}\n" \
                f"Found {len(matches)} matches ({len(files)} files, {len(dirs)} directories)\n\n"

        if dirs:
            result += "Directories:\n"
            for d in dirs:
                result += f"  DIR  {d.relative_to(root)}/\n"
            result += "\n"

        if files:
            result += "Files:\n"
            for f in files:
                size = f.stat().st_size
                result += f"  FILE {size:>10} {f.relative_to(root)}\n"

        return result

    except Exception as e:
        return f"Error performing glob search: {str(e)}"
