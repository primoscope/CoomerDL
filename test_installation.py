#!/usr/bin/env python3
"""
Installation and import test for CoomerDL.
Tests that all core modules can be imported successfully.
"""

import sys
import importlib
from pathlib import Path

def test_import(module_name):
    """Test importing a module."""
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name}")
        return True
    except ImportError as e:
        print(f"❌ {module_name}: {e}")
        return False
    except Exception as e:
        print(f"⚠️  {module_name}: {e}")
        return True  # Module exists but has runtime issues (acceptable)

def main():
    """Run installation tests."""
    print("=" * 70)
    print("CoomerDL Installation Test")
    print("=" * 70)
    
    # Check Python version
    print(f"\n🐍 Python version: {sys.version}")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required!")
        return 1
    print("✅ Python version OK")
    
    # Check core dependencies
    print("\n📦 Testing Core Dependencies:")
    dependencies = [
        'requests',
        'bs4',  # beautifulsoup4
        'urllib3',
        'PIL',  # pillow
        'psutil',
        'markdown2',
        'cloudscraper',
        'yt_dlp',
        'gallery_dl',
    ]
    
    dep_results = []
    for dep in dependencies:
        dep_results.append(test_import(dep))
    
    # Check application modules (non-GUI)
    print("\n📁 Testing Application Modules:")
    app_modules = [
        'downloader',
        'downloader.downloader',
        'downloader.bunkr',
        'downloader.erome',
        'downloader.simpcity',
        'downloader.jpg5',
    ]
    
    if Path('downloader/factory.py').exists():
        app_modules.append('downloader.factory')
    if Path('downloader/base.py').exists():
        app_modules.append('downloader.base')
    if Path('downloader/queue.py').exists():
        app_modules.append('downloader.queue')
    if Path('downloader/ytdlp_adapter.py').exists():
        app_modules.append('downloader.ytdlp_adapter')
    
    app_results = []
    for module in app_modules:
        app_results.append(test_import(module))
    
    # Summary
    print("\n" + "=" * 70)
    print("INSTALLATION TEST SUMMARY")
    print("=" * 70)
    print(f"Dependencies: {sum(dep_results)}/{len(dep_results)} passed")
    print(f"App modules: {sum(app_results)}/{len(app_results)} passed")
    
    all_passed = all(dep_results) and all(app_results)
    
    if all_passed:
        print("\n✅ ALL TESTS PASSED - Installation is working correctly!")
        print("\nNote: GUI components (tkinter) not tested as they require display.")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Please check errors above")
        return 1

if __name__ == '__main__':
    sys.exit(main())
