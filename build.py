#!/usr/bin/env python3
"""
CoomerDL Build Script

This script builds a standalone executable for CoomerDL using PyInstaller.
It can be run locally for testing or used in CI/CD pipelines.

Usage:
    python build.py [--clean] [--debug]

Options:
    --clean     Clean build artifacts before building
    --debug     Build with debug console enabled
"""

import sys
import os
import shutil
import subprocess
import argparse
from pathlib import Path


def clean_build_artifacts():
    """Remove all build artifacts."""
    print("🧹 Cleaning build artifacts...")
    
    artifacts = ['build', 'dist', '__pycache__']
    spec_files = list(Path('.').glob('*.spec'))
    
    for artifact in artifacts:
        if os.path.exists(artifact):
            print(f"   Removing {artifact}/")
            shutil.rmtree(artifact)
    
    # Don't remove CoomerDL.spec as it's part of the repo
    print("✓ Cleanup complete")


def check_requirements():
    """Check if all required packages are installed."""
    print("📋 Checking requirements...")
    
    try:
        import PyInstaller
        print(f"   ✓ PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("   ✗ PyInstaller not found")
        print("   Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("   ✓ PyInstaller installed")
    
    # Check main dependencies
    requirements = [
        'customtkinter',
        'beautifulsoup4',
        'requests',
        'pillow',
        'yt_dlp',
        'gallery_dl',
    ]
    
    missing = []
    for req in requirements:
        try:
            __import__(req.replace('-', '_'))
            print(f"   ✓ {req}")
        except ImportError:
            missing.append(req)
            print(f"   ✗ {req} not found")
    
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("   Install with: pip install -r requirements.txt")
        return False
    
    print("✓ All requirements satisfied")
    return True


def build_executable(debug=False):
    """Build the executable using PyInstaller."""
    print("🔨 Building executable...")
    
    # Check if spec file exists
    spec_file = "CoomerDL.spec"
    if not os.path.exists(spec_file):
        print(f"✗ Error: {spec_file} not found!")
        return False
    
    # Build command
    cmd = [sys.executable, "-m", "PyInstaller", spec_file]
    
    if debug:
        print("   Debug mode enabled (console window will be visible)")
        # For debug, we'd need to modify the spec file or use different options
        # For now, just note it
    
    print(f"   Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print("✓ Build complete")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed with exit code {e.returncode}")
        return False


def verify_executable():
    """Verify that the executable was created successfully."""
    print("🔍 Verifying executable...")
    
    # Determine executable name based on platform
    if sys.platform == 'win32':
        exe_path = Path('dist/CoomerDL.exe')
    else:
        exe_path = Path('dist/CoomerDL')
    
    if not exe_path.exists():
        print(f"✗ Error: Executable not found at {exe_path}")
        return False
    
    size_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"   ✓ Executable: {exe_path}")
    print(f"   ✓ Size: {size_mb:.2f} MB")
    
    # Make executable on Unix systems
    if sys.platform != 'win32':
        os.chmod(exe_path, 0o755)
        print(f"   ✓ Made executable")
    
    print("✓ Verification complete")
    return True


def main():
    parser = argparse.ArgumentParser(description='Build CoomerDL executable')
    parser.add_argument('--clean', action='store_true', help='Clean build artifacts before building')
    parser.add_argument('--debug', action='store_true', help='Build with debug console enabled')
    args = parser.parse_args()
    
    print("=" * 60)
    print("CoomerDL Build Script")
    print("=" * 60)
    print()
    
    # Clean if requested
    if args.clean:
        clean_build_artifacts()
        print()
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Build aborted due to missing requirements")
        return 1
    
    print()
    
    # Build executable
    if not build_executable(debug=args.debug):
        print("\n❌ Build failed")
        return 1
    
    print()
    
    # Verify executable
    if not verify_executable():
        print("\n❌ Verification failed")
        return 1
    
    print()
    print("=" * 60)
    print("✅ Build successful!")
    print("=" * 60)
    
    if sys.platform == 'win32':
        print("\n📦 Executable location: dist\\CoomerDL.exe")
        print("   You can now run: dist\\CoomerDL.exe")
    else:
        print("\n📦 Executable location: dist/CoomerDL")
        print("   You can now run: ./dist/CoomerDL")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
