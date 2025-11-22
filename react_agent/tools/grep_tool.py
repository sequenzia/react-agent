"""Grep text search tool."""

import re
from pathlib import Path
from typing import Optional
from langchain.tools import tool


@tool
def grep_search(
    pattern: str,
    path: str = ".",
    file_pattern: str = "*",
    case_sensitive: bool = False,
    max_results: int = 100
) -> str:
    """Search for text pattern in files (similar to grep).

    Args:
        pattern: Regular expression pattern to search for
        path: Directory or file to search in (default: current directory)
        file_pattern: Glob pattern for files to search (default: all files)
        case_sensitive: Whether search is case sensitive (default: False)
        max_results: Maximum number of results to return (default: 100)

    Returns:
        Matching lines with file names and line numbers

    Examples:
        grep_search("TODO", path="src")
        grep_search("def.*test", file_pattern="*.py")
        grep_search("error", case_sensitive=True)
    """
    try:
        search_path = Path(path).expanduser().resolve()

        if not search_path.exists():
            return f"Error: Path not found: {path}"

        # Compile regex pattern
        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            regex = re.compile(pattern, flags)
        except re.error as e:
            return f"Error: Invalid regex pattern: {str(e)}"

        results = []
        files_searched = 0

        # Determine files to search
        if search_path.is_file():
            files_to_search = [search_path]
        else:
            files_to_search = list(search_path.rglob(file_pattern))
            files_to_search = [f for f in files_to_search if f.is_file()]

        for file_path in files_to_search:
            # Skip binary files and common non-text files
            if file_path.suffix in ['.pyc', '.so', '.o', '.a', '.exe', '.dll', '.bin']:
                continue

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        if regex.search(line):
                            # Get relative path for cleaner output
                            if search_path.is_dir():
                                rel_path = file_path.relative_to(search_path)
                            else:
                                rel_path = file_path.name

                            results.append({
                                'file': str(rel_path),
                                'line': line_num,
                                'content': line.rstrip()
                            })

                            if len(results) >= max_results:
                                break

                files_searched += 1

                if len(results) >= max_results:
                    break

            except (PermissionError, UnicodeDecodeError):
                # Skip files we can't read
                continue

        if not results:
            return f"No matches found for pattern: {pattern}\n" \
                   f"Searched {files_searched} files in: {path}"

        # Format results
        output = f"Grep search: {pattern}\n" \
                f"Path: {path}\n" \
                f"Files searched: {files_searched}\n" \
                f"Matches found: {len(results)}"

        if len(results) >= max_results:
            output += f" (limited to {max_results})"

        output += "\n\n"

        # Group by file
        current_file = None
        for result in results:
            if result['file'] != current_file:
                current_file = result['file']
                output += f"\n{current_file}:\n"

            output += f"  {result['line']:4d}: {result['content']}\n"

        return output

    except Exception as e:
        return f"Error performing grep search: {str(e)}"
