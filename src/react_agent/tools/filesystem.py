"""Filesystem tools for reading and writing files."""

import os
from pathlib import Path
from typing import Optional
from langchain.tools import tool


@tool
def read_file(file_path: str, encoding: str = "utf-8") -> str:
    """Read the contents of a file.

    Args:
        file_path: Path to the file to read
        encoding: File encoding (default: utf-8)

    Returns:
        Contents of the file as a string

    Examples:
        read_file("README.md")
        read_file("/path/to/file.txt")
    """
    try:
        path = Path(file_path).expanduser().resolve()

        if not path.exists():
            return f"Error: File not found: {file_path}"

        if not path.is_file():
            return f"Error: Path is not a file: {file_path}"

        with open(path, 'r', encoding=encoding) as f:
            content = f.read()

        return f"File: {file_path}\n" \
               f"Size: {len(content)} characters\n" \
               f"Lines: {len(content.splitlines())}\n\n" \
               f"{content}"

    except PermissionError:
        return f"Error: Permission denied reading file: {file_path}"
    except UnicodeDecodeError:
        return f"Error: Unable to decode file with encoding {encoding}: {file_path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool
def write_file(file_path: str, content: str, encoding: str = "utf-8", mode: str = "w") -> str:
    """Write content to a file.

    Args:
        file_path: Path to the file to write
        content: Content to write to the file
        encoding: File encoding (default: utf-8)
        mode: Write mode - 'w' to overwrite, 'a' to append (default: w)

    Returns:
        Success or error message

    Examples:
        write_file("output.txt", "Hello, World!")
        write_file("log.txt", "New entry\\n", mode="a")
    """
    try:
        path = Path(file_path).expanduser().resolve()

        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, mode, encoding=encoding) as f:
            f.write(content)

        action = "Appended to" if mode == "a" else "Wrote to"
        return f"{action} file: {file_path}\n" \
               f"Size: {len(content)} characters\n" \
               f"Lines: {len(content.splitlines())}"

    except PermissionError:
        return f"Error: Permission denied writing to file: {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


@tool
def list_directory(
    directory_path: str = ".",
    show_hidden: bool = False,
    recursive: bool = False
) -> str:
    """List contents of a directory.

    Args:
        directory_path: Path to the directory (default: current directory)
        show_hidden: Whether to show hidden files (default: False)
        recursive: Whether to list recursively (default: False)

    Returns:
        Formatted list of directory contents

    Examples:
        list_directory(".")
        list_directory("/path/to/dir", show_hidden=True)
        list_directory("src", recursive=True)
    """
    try:
        path = Path(directory_path).expanduser().resolve()

        if not path.exists():
            return f"Error: Directory not found: {directory_path}"

        if not path.is_dir():
            return f"Error: Path is not a directory: {directory_path}"

        entries = []

        if recursive:
            # Recursive listing
            for item in path.rglob("*"):
                if not show_hidden and item.name.startswith("."):
                    continue

                rel_path = item.relative_to(path)
                item_type = "DIR" if item.is_dir() else "FILE"
                size = item.stat().st_size if item.is_file() else "-"

                entries.append(f"{item_type:5} {size:>10} {rel_path}")
        else:
            # Single level listing
            for item in sorted(path.iterdir()):
                if not show_hidden and item.name.startswith("."):
                    continue

                item_type = "DIR" if item.is_dir() else "FILE"
                size = item.stat().st_size if item.is_file() else "-"

                entries.append(f"{item_type:5} {size:>10} {item.name}")

        if not entries:
            return f"Directory is empty: {directory_path}"

        header = f"Directory: {directory_path}\n" \
                f"{'Type':<5} {'Size':>10} Name\n" \
                f"{'-' * 50}"

        return header + "\n" + "\n".join(entries)

    except PermissionError:
        return f"Error: Permission denied accessing directory: {directory_path}"
    except Exception as e:
        return f"Error listing directory: {str(e)}"
