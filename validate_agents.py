#!/usr/bin/env python3
"""
Validation script for GitHub Copilot/Gemini AI Agent configurations.
Tests that all agent files are properly formatted and contain required fields.
"""

import os
import re
import sys
from pathlib import Path

def validate_agent_file(filepath):
    """Validate a single agent configuration file."""
    print(f"\n📄 Validating: {filepath.name}")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    errors = []
    warnings = []
    
    # Check for frontmatter
    if not content.startswith('---'):
        errors.append("Missing frontmatter delimiter at start")
    
    # Extract frontmatter
    frontmatter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("Invalid frontmatter format")
        return errors, warnings
    
    frontmatter = frontmatter_match.group(1)
    
    # Required fields
    required_fields = ['name', 'description']
    for field in required_fields:
        if f'{field}:' not in frontmatter:
            errors.append(f"Missing required field: {field}")
    
    # Check for tools field
    if 'tools:' not in frontmatter:
        warnings.append("No 'tools' field specified")
    
    # Check for metadata field
    if 'metadata:' not in frontmatter:
        warnings.append("No 'metadata' field specified")
    
    # Validate name format
    name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not name:
            errors.append("Agent name is empty")
        else:
            print(f"  ✓ Agent name: {name}")
    
    # Validate description
    desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip()
        if not desc:
            errors.append("Agent description is empty")
        else:
            print(f"  ✓ Description: {desc[:60]}...")
    
    # Check content length
    body = content[frontmatter_match.end():]
    if len(body.strip()) < 100:
        warnings.append("Agent documentation seems very short")
    else:
        print(f"  ✓ Documentation length: {len(body)} characters")
    
    return errors, warnings

def main():
    """Main validation function."""
    print("=" * 70)
    print("GitHub Copilot/Gemini Agent Configuration Validator")
    print("=" * 70)
    
    # Find all agent files
    agents_dir = Path('.github/agents')
    if not agents_dir.exists():
        print(f"\n❌ ERROR: {agents_dir} directory not found!")
        return 1
    
    print(f"\n📁 Searching for agent files in: {agents_dir}")
    agent_files = list(agents_dir.glob('*.agent.md'))
    
    if not agent_files:
        print("\n⚠️  WARNING: No .agent.md files found!")
        return 1
    
    print(f"✓ Found {len(agent_files)} agent file(s)")
    
    all_errors = []
    all_warnings = []
    
    # Validate each agent file
    for agent_file in sorted(agent_files):
        errors, warnings = validate_agent_file(agent_file)
        
        if errors:
            print(f"  ❌ ERRORS ({len(errors)}):")
            for error in errors:
                print(f"     - {error}")
            all_errors.extend(errors)
        else:
            print(f"  ✅ No errors found")
        
        if warnings:
            print(f"  ⚠️  WARNINGS ({len(warnings)}):")
            for warning in warnings:
                print(f"     - {warning}")
            all_warnings.extend(warnings)
    
    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Agent files checked: {len(agent_files)}")
    print(f"Total errors: {len(all_errors)}")
    print(f"Total warnings: {len(all_warnings)}")
    
    if all_errors:
        print("\n❌ VALIDATION FAILED - Please fix the errors above")
        return 1
    elif all_warnings:
        print("\n⚠️  VALIDATION PASSED WITH WARNINGS")
        return 0
    else:
        print("\n✅ ALL VALIDATIONS PASSED")
        return 0

if __name__ == '__main__':
    sys.exit(main())
