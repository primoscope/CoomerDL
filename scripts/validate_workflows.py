#!/usr/bin/env python3
"""
Workflow Validation Script

This script validates the GitHub Actions workflows to ensure they are properly
configured and will work correctly.
"""

import os
import sys
import yaml
from pathlib import Path


def validate_yaml_syntax(file_path):
    """Validate YAML file syntax."""
    try:
        with open(file_path, 'r') as f:
            yaml.safe_load(f)
        return True, None
    except yaml.YAMLError as e:
        return False, str(e)


def check_workflow_file(file_path):
    """Perform comprehensive checks on a workflow file."""
    print(f"\n{'='*60}")
    print(f"Checking: {file_path}")
    print('='*60)
    
    # Check file exists
    if not os.path.exists(file_path):
        print(f"✗ File not found: {file_path}")
        return False
    
    # Validate YAML syntax
    valid, error = validate_yaml_syntax(file_path)
    if not valid:
        print(f"✗ YAML syntax error: {error}")
        return False
    print("✓ YAML syntax is valid")
    
    # Load and validate structure
    with open(file_path, 'r') as f:
        workflow = yaml.safe_load(f)
    
    # Check required top-level keys
    required_keys = ['name', 'jobs']
    for key in required_keys:
        if key not in workflow:
            print(f"✗ Missing required key: {key}")
            return False
    
    # Check 'on' key (can also be True in YAML, so check both)
    if 'on' not in workflow and True not in workflow:
        print("✗ Missing required key: on")
        return False
    
    print(f"✓ Has required keys: name, on, jobs")
    
    # Check jobs
    if not workflow['jobs']:
        print("✗ No jobs defined")
        return False
    
    print(f"✓ Contains {len(workflow['jobs'])} job(s):")
    for job_name in workflow['jobs']:
        print(f"  - {job_name}")
    
    # Check each job has required fields
    for job_name, job in workflow['jobs'].items():
        if 'runs-on' not in job and 'needs' not in job:
            print(f"✗ Job '{job_name}' missing 'runs-on'")
            return False
        if 'steps' not in job:
            print(f"✗ Job '{job_name}' missing 'steps'")
            return False
    print("✓ All jobs have required fields")
    
    return True


def check_release_workflow():
    """Check release workflow specific requirements."""
    file_path = '.github/workflows/release.yml'
    
    if not os.path.exists(file_path):
        return True  # Skip if file doesn't exist
    
    with open(file_path, 'r') as f:
        workflow = yaml.safe_load(f)
    
    print(f"\n{'='*60}")
    print("Release Workflow Specific Checks")
    print('='*60)
    
    # Check if triggered by tags
    on_config = workflow.get('on', workflow.get(True, {}))
    push_config = on_config.get('push', {})
    tags = push_config.get('tags', [])
    
    if not tags:
        print("⚠ Warning: Release workflow not triggered by tags")
        print("  Consider adding: on.push.tags: ['v*']")
    else:
        print(f"✓ Triggered by tags: {tags}")
    
    # Check for GitHub token permissions
    jobs = workflow.get('jobs', {})
    release_job = None
    for job_name, job in jobs.items():
        if 'release' in job_name.lower() or 'create' in job_name.lower():
            release_job = job
            break
    
    if release_job:
        print("✓ Found release creation job")
        
        # Check for artifact upload
        steps = release_job.get('steps', [])
        has_release_step = False
        for step in steps:
            uses = step.get('uses', '')
            if 'gh-release' in uses or 'create-release' in uses:
                has_release_step = True
                break
        
        if has_release_step:
            print("✓ Has release creation step")
        else:
            print("⚠ Warning: No release creation step found")
    
    return True


def check_spec_file():
    """Check PyInstaller spec file."""
    spec_file = 'CoomerDL.spec'
    
    print(f"\n{'='*60}")
    print(f"Checking: {spec_file}")
    print('='*60)
    
    if not os.path.exists(spec_file):
        print(f"✗ File not found: {spec_file}")
        return False
    
    print("✓ Spec file exists")
    
    # Check Python syntax
    try:
        with open(spec_file, 'r') as f:
            content = f.read()
        compile(content, spec_file, 'exec')
        print("✓ Valid Python syntax")
    except SyntaxError as e:
        print(f"✗ Syntax error: {e}")
        return False
    
    # Check for required components
    required_patterns = [
        ('Analysis', 'Analysis configuration'),
        ('PYZ', 'PYZ configuration'),
        ('EXE', 'EXE configuration'),
        ('main.py', 'Entry point reference'),
    ]
    
    for pattern, description in required_patterns:
        if pattern in content:
            print(f"✓ Contains {description}")
        else:
            print(f"✗ Missing {description}")
            return False
    
    return True


def check_build_script():
    """Check build.py script."""
    build_script = 'build.py'
    
    print(f"\n{'='*60}")
    print(f"Checking: {build_script}")
    print('='*60)
    
    if not os.path.exists(build_script):
        print(f"✗ File not found: {build_script}")
        return False
    
    print("✓ Build script exists")
    
    # Check Python syntax
    try:
        with open(build_script, 'r') as f:
            content = f.read()
        compile(content, build_script, 'exec')
        print("✓ Valid Python syntax")
    except SyntaxError as e:
        print(f"✗ Syntax error: {e}")
        return False
    
    # Check for required functions
    required_functions = [
        'check_requirements',
        'build_executable',
        'verify_executable',
    ]
    
    for func in required_functions:
        if f'def {func}' in content:
            print(f"✓ Contains {func}() function")
        else:
            print(f"⚠ Missing {func}() function")
    
    return True


def check_project_structure():
    """Check project has required files and directories."""
    print(f"\n{'='*60}")
    print("Project Structure Check")
    print('='*60)
    
    required_files = [
        'main.py',
        'requirements.txt',
        'README.md',
        'CoomerDL.spec',
        'build.py',
    ]
    
    required_dirs = [
        'resources',
        'app',
        'downloader',
        '.github/workflows',
    ]
    
    all_ok = True
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ Missing: {file}")
            all_ok = False
    
    for directory in required_dirs:
        if os.path.isdir(directory):
            print(f"✓ {directory}/")
        else:
            print(f"✗ Missing: {directory}/")
            all_ok = False
    
    return all_ok


def main():
    print("="*60)
    print("GitHub Actions Workflow Validation")
    print("="*60)
    
    # Change to the repository root if running from scripts/
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent if script_dir.name == 'scripts' else script_dir
    os.chdir(repo_root)
    print(f"\nWorking directory: {os.getcwd()}\n")
    
    all_passed = True
    
    # Check workflows
    workflows = [
        '.github/workflows/ci.yml',
        '.github/workflows/release.yml',
    ]
    
    for workflow in workflows:
        if not check_workflow_file(workflow):
            all_passed = False
    
    # Check release workflow specifics
    if not check_release_workflow():
        all_passed = False
    
    # Check spec file
    if not check_spec_file():
        all_passed = False
    
    # Check build script
    if not check_build_script():
        all_passed = False
    
    # Check project structure
    if not check_project_structure():
        all_passed = False
    
    # Summary
    print(f"\n{'='*60}")
    print("Validation Summary")
    print('='*60)
    
    if all_passed:
        print("✅ All checks passed!")
        print("\nYour workflows are ready to use:")
        print("1. CI workflow will run on every push/PR")
        print("2. Release workflow will run when you push a version tag")
        print("\nTo create a release:")
        print("  git tag -a v1.0.0 -m 'Release v1.0.0'")
        print("  git push origin v1.0.0")
        return 0
    else:
        print("❌ Some checks failed")
        print("Please fix the issues above before proceeding")
        return 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
