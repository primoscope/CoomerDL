"""
Unit tests for Dashboard UI components integration.

Tests verify that UI components can be imported and have expected structure.
These tests are designed to work in headless environments where tkinter may not be available.

Note: These tests may be affected by other tests that mock tkinter globally (e.g., test_utils.py).
In such cases, the tests will skip gracefully or handle mocked imports appropriately.
"""
import pytest


def is_tkinter_available():
    """Check if real tkinter (not a mock) is available."""
    try:
        import tkinter
        # Check if tkinter module has been mocked (by test_utils.py or similar)
        # MagicMock objects have a _mock_name attribute
        if hasattr(tkinter, '_mock_name'):
            return False
        # Try to access a real tkinter attribute to verify it's functional
        tkinter.Tk
        return True
    except (ImportError, AttributeError):
        return False


class TestDashboardImports:
    """Test that dashboard-related components can be imported."""
    
    def test_command_center_dashboard_import(self):
        """Test CommandCenterDashboard can be imported."""
        if not is_tkinter_available():
            pytest.skip("tkinter not available or is mocked")
        from app.window.dashboard import CommandCenterDashboard
        assert CommandCenterDashboard is not None
    
    def test_menu_bar_import(self):
        """Test MenuBar can be imported."""
        if not is_tkinter_available():
            pytest.skip("tkinter not available or is mocked")
        from app.window.menu_bar import MenuBar
        assert MenuBar is not None
    
    def test_queue_dialog_import(self):
        """Test QueueDialog can be imported."""
        if not is_tkinter_available():
            pytest.skip("tkinter not available or is mocked")
        from app.dialogs.queue_dialog import QueueDialog
        assert QueueDialog is not None
    
    def test_download_queue_import(self):
        """Test DownloadQueue can be imported."""
        from app.models.download_queue import DownloadQueue
        assert DownloadQueue is not None


class TestDashboardStructure:
    """Test dashboard component structure."""
    
    def test_dashboard_has_required_methods(self):
        """Test that CommandCenterDashboard has all required methods."""
        if not is_tkinter_available():
            pytest.skip("tkinter not available or is mocked")
        from app.window.dashboard import CommandCenterDashboard
        
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
            assert hasattr(CommandCenterDashboard, method), \
                f"CommandCenterDashboard missing method: {method}"


class TestModularComponents:
    """Test that modular UI components are properly structured."""
    
    @pytest.mark.parametrize("module_name,class_name", [
        ('app.window.input_panel', 'InputPanel'),
        ('app.window.options_panel', 'OptionsPanel'),
        ('app.window.action_panel', 'ActionPanel'),
        ('app.window.log_panel', 'LogPanel'),
        ('app.window.progress_panel', 'ProgressPanel'),
        ('app.window.status_bar', 'StatusBar'),
        ('app.window.gallery_viewer', 'GalleryViewer'),
        ('app.window.history_viewer', 'HistoryViewer'),
    ])
    def test_component_can_be_imported(self, module_name, class_name):
        """Test that each modular component can be imported."""
        if not is_tkinter_available():
            pytest.skip("tkinter not available or is mocked")
        module = __import__(module_name, fromlist=[class_name])
        assert hasattr(module, class_name), \
            f"Module {module_name} does not have class {class_name}"
