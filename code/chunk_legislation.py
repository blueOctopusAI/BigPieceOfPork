import os
import re
from typing import Dict, Any

# Configuration
INPUT_FILE = "cleaned_output.txt"
OUTPUT_DIR = "chunks"
DEFAULT_MAX_CHARS = 20000  # Default maximum characters per chunk file

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Regex patterns to identify division and title lines
division_pattern = re.compile(r'^DIVISION\s+([A-Z]+)\b', re.IGNORECASE)
title_pattern = re.compile(r'^TITLE\s+([IVXLC]+)\b', re.IGNORECASE)

def write_chunk(lines_list: list, div: str, tit: str, chunk_num: int, max_chars: int) -> None:
    """Write out the current chunk to one or more files without exceeding max_chars."""
    if not lines_list:
        return

    # Determine filename base parts
    filename_parts = [f"{chunk_num:03d}"]
    if div:
        filename_parts.append("division")
        filename_parts.append(div.lower())
    if tit:
        filename_parts.append("title")
        filename_parts.append(tit.lower())
    base_filename = "_".join(filename_parts)

    # Join lines into a single string
    content = "\n".join(lines_list)

    # If it fits in one file
    if len(content) <= max_chars:
        filepath = os.path.join(OUTPUT_DIR, base_filename + ".txt")
        with open(filepath, "w", encoding="utf-8") as outfile:
            outfile.write(content)
    else:
        # Split into multiple parts
        part_number = 1
        start = 0
        while start < len(content):
            end = start + max_chars
            chunk_content = content[start:end]
            part_filename = f"{base_filename}_part{part_number}.txt"
            filepath = os.path.join(OUTPUT_DIR, part_filename)
            with open(filepath, "w", encoding="utf-8") as outfile:
                outfile.write(chunk_content)
            start = end
            part_number += 1

def chunk_by_size(lines: list, max_chars: int) -> None:
    """Split text into chunks based on size while respecting structure."""
    current_chunk_lines = []
    chunk_count = 0
    current_size = 0

    for line in lines:
        line_size = len(line) + 1  # +1 for newline
        if current_size + line_size > max_chars and current_chunk_lines:
            chunk_count += 1
            write_chunk(current_chunk_lines, None, None, chunk_count, max_chars)
            current_chunk_lines = []
            current_size = 0

        current_chunk_lines.append(line)
        current_size += line_size

    # Write final chunk if any
    if current_chunk_lines:
        chunk_count += 1
        write_chunk(current_chunk_lines, None, None, chunk_count, max_chars)

def chunk_by_structure(lines: list) -> None:
    """Split text into chunks based on DIVISION and TITLE markers."""
    current_chunk_lines = []
    chunk_count = 0
    current_division = None
    current_title = None

    def start_new_chunk():
        nonlocal current_chunk_lines, chunk_count
        if current_chunk_lines:
            chunk_count += 1
            write_chunk(current_chunk_lines, current_division, current_title, 
                       chunk_count, DEFAULT_MAX_CHARS)
            current_chunk_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current_chunk_lines:
                current_chunk_lines.append("")
            continue

        div_match = division_pattern.match(stripped)
        title_match = title_pattern.match(stripped)

        if div_match:
            start_new_chunk()
            current_division = div_match.group(1)
            current_title = None
            current_chunk_lines.append(stripped)
        elif title_match:
            start_new_chunk()
            current_title = title_match.group(1)
            current_chunk_lines.append(stripped)
        else:
            current_chunk_lines.append(stripped)

    start_new_chunk()

def process_with_options(options: Dict[str, Any]) -> None:
    """Process the text file according to specified chunking strategy."""
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Clean up lines
    lines = [line.rstrip() for line in lines]

    # Choose chunking strategy
    if options.get("strategy", "size") == "structure":
        print("Using structure-based chunking strategy...")
        chunk_by_structure(lines)
    else:
        print(f"Using size-based chunking strategy (max {options.get('max_chars', DEFAULT_MAX_CHARS)} chars)...")
        chunk_by_size(lines, options.get('max_chars', DEFAULT_MAX_CHARS))

    print("Chunking complete. Check the 'chunks' directory for output files.")

# Default behavior when run directly
if __name__ == "__main__":
    process_with_options({"strategy": "size", "max_chars": DEFAULT_MAX_CHARS})