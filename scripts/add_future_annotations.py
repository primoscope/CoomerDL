#!/usr/bin/env python3
"""
Script to add 'from __future__ import annotations' to all Python files.
"""

import os
import sys
from pathlib import Path


def add_future_annotations(filepath: Path) -> bool:
    """
    Add 'from __future__ import annotations' to a Python file if not present.
    
    Args:
        filepath: Path to the Python file
        
    Returns:
        True if file was modified, False otherwise
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False
    
    # Check if already has future annotations
    for line in lines:
        if 'from __future__ import annotations' in line:
            return False
    
    # Find where to insert (after docstring and before first import)
    insert_index = 0
    in_docstring = False
    docstring_char = None
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Skip empty lines and comments at the start
        if not stripped or stripped.startswith('#'):
            insert_index = i + 1
            continue
        
        # Handle docstrings
        if not in_docstring:
            if stripped.startswith('"""') or stripped.startswith("'''"):
                docstring_char = stripped[:3]
                in_docstring = True
                # Check if it's a one-line docstring
                if stripped.count(docstring_char) >= 2:
                    in_docstring = False
                    insert_index = i + 1
                continue
        else:
            if docstring_char in line:
                in_docstring = False
                insert_index = i + 1
                continue
        
        # Stop at first import or code line
        if stripped.startswith('import ') or stripped.startswith('from '):
            break
        if not in_docstring and stripped:
            break
    
    # Insert the import
    new_lines = lines[:insert_index]
    new_lines.append('from __future__ import annotations\n')
    if insert_index < len(lines) and lines[insert_index].strip():
        new_lines.append('\n')
    new_lines.extend(lines[insert_index:])
    
    # Write back
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        return True
    except Exception as e:
        print(f"Error writing {filepath}: {e}")
        return False


def process_directory(directory: Path) -> tuple[int, int]:
    """
    Process all Python files in a directory recursively.
    
    Args:
        directory: Directory to process
        
    Returns:
        Tuple of (files_processed, files_modified)
    """
    processed = 0
    modified = 0
    
    for py_file in directory.rglob('*.py'):
        # Skip __pycache__ and venv directories
        if '__pycache__' in str(py_file) or 'venv' in str(py_file) or '.venv' in str(py_file):
            continue
        
        processed += 1
        if add_future_annotations(py_file):
            modified += 1
            print(f"✅ Modified: {py_file}")
        else:
            print(f"⏭️  Skipped: {py_file}")
    
    return processed, modified


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
    else:
        target = Path.cwd()
    
    if not target.exists():
        print(f"Error: {target} does not exist")
        return 1
    
    print(f"🔍 Processing Python files in: {target}")
    print("-" * 60)
    
    processed, modified = process_directory(target)
    
    print("-" * 60)
    print(f"📊 Summary:")
    print(f"   Files processed: {processed}")
    print(f"   Files modified: {modified}")
    print(f"   Files skipped: {processed - modified}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
