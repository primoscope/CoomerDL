#!/usr/bin/env python3
"""
Test script to verify CommandCenterDashboard component works correctly.
This script can be run in a headless environment to check for import errors.
"""

import sys
import os
import traceback

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_dashboard_imports():
    """Test that all dashboard-related imports work."""
    print("Testing dashboard imports...")
    
    try:
        from app.window.dashboard import CommandCenterDashboard
        print("✓ CommandCenterDashboard imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import CommandCenterDashboard: {e}")
        return False
    
    try:
        from app.window.menu_bar import MenuBar
        print("✓ MenuBar imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import MenuBar: {e}")
        return False
    
    try:
        from app.dialogs.queue_dialog import QueueDialog
        print("✓ QueueDialog imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import QueueDialog: {e}")
        return False
    
    try:
        from app.models.download_queue import DownloadQueue
        print("✓ DownloadQueue imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import DownloadQueue: {e}")
        return False
    
    return True


def test_dashboard_structure():
    """Test that dashboard has expected structure."""
    print("\nTesting dashboard structure...")
    
    # Since we can't actually create GUI widgets in headless mode,
    # we'll just verify the class structure
    from app.window.dashboard import CommandCenterDashboard
    
    # Check that required methods exist
    expected_methods = [
        'create_home_tab',
        'create_queue_tab',
        'create_gallery_tab',
        'create_history_tab',
        'create_stat_card',
        'start_download',
        'update_stats'
    ]
    
    for method in expected_methods:
        if hasattr(CommandCenterDashboard, method):
            print(f"✓ Method '{method}' exists")
        else:
            print(f"✗ Method '{method}' missing")
            return False
    
    return True


def test_modular_components():
    """Test that all modular UI components are importable."""
    print("\nTesting modular UI components...")
    
    components = [
        ('app.window.input_panel', 'InputPanel'),
        ('app.window.options_panel', 'OptionsPanel'),
        ('app.window.action_panel', 'ActionPanel'),
        ('app.window.log_panel', 'LogPanel'),
        ('app.window.progress_panel', 'ProgressPanel'),
        ('app.window.status_bar', 'StatusBar'),
        ('app.window.gallery_viewer', 'GalleryViewer'),
        ('app.window.history_viewer', 'HistoryViewer'),
    ]
    
    for module_name, class_name in components:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"✓ {class_name} imported successfully")
        except ImportError as e:
            print(f"✗ Failed to import {class_name}: {e}")
            return False
        except AttributeError as e:
            print(f"✗ Class {class_name} not found in {module_name}: {e}")
            return False
    
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Dashboard Component Integration Test")
    print("=" * 60)
    
    tests = [
        test_dashboard_imports,
        test_dashboard_structure,
        test_modular_components,
    ]
    
    all_passed = True
    for test in tests:
        try:
            if not test():
                all_passed = False
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            traceback.print_exc()
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed!")
        print("=" * 60)
        return 0
    else:
        print("✗ Some tests failed")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
