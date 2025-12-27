"""
Tests for settings persistence.
Tests loading and saving configuration without modifying the source code.
"""
import pytest
import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Mock all GUI-related modules before importing app modules
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['customtkinter'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['PIL.ImageTk'] = MagicMock()

from app.settings_window import SettingsWindow


class TestSettingsPersistence:
    """Test settings loading and saving functionality."""
    
    def setup_method(self):
        """Set up test fixtures before each test."""
        # Create mock parent and functions
        self.mock_parent = MagicMock()
        self.mock_translate = lambda x, **kwargs: x
        self.mock_load_translations = MagicMock()
        self.mock_update_ui_texts = MagicMock()
        self.mock_save_language_preference = MagicMock()
        self.mock_check_for_new_version = MagicMock()
    
    def test_load_settings_default_values(self, tmp_path):
        """Test that load_settings returns defaults when file doesn't exist."""
        # Temporarily change CONFIG_PATH to non-existent location
        original_path = SettingsWindow.CONFIG_PATH
        SettingsWindow.CONFIG_PATH = str(tmp_path / "nonexistent" / "settings.json")
        
        try:
            settings_window = SettingsWindow(
                parent=self.mock_parent,
                translate=self.mock_translate,
                load_translations_func=self.mock_load_translations,
                update_ui_texts_func=self.mock_update_ui_texts,
                save_language_preference_func=self.mock_save_language_preference,
                version="1.0.0",
                downloader=None,
                check_for_new_version_func=self.mock_check_for_new_version
            )
            
            settings = settings_window.load_settings()
            
            # Check default values
            assert settings['max_downloads'] == 3
            assert settings['folder_structure'] == 'default'
            assert settings['language'] == 'en'
            assert settings['theme'] == 'System'
        finally:
            SettingsWindow.CONFIG_PATH = original_path
    
    def test_save_and_load_settings(self, tmp_path):
        """Test saving settings to file and loading them back."""
        config_file = tmp_path / "config" / "settings.json"
        original_path = SettingsWindow.CONFIG_PATH
        SettingsWindow.CONFIG_PATH = str(config_file)
        
        try:
            settings_window = SettingsWindow(
                parent=self.mock_parent,
                translate=self.mock_translate,
                load_translations_func=self.mock_load_translations,
                update_ui_texts_func=self.mock_update_ui_texts,
                save_language_preference_func=self.mock_save_language_preference,
                version="1.0.0",
                downloader=None,
                check_for_new_version_func=self.mock_check_for_new_version
            )
            
            # Modify settings
            settings_window.settings['max_downloads'] = 5
            settings_window.settings['folder_structure'] = 'custom'
            settings_window.settings['language'] = 'es'
            settings_window.settings['theme'] = 'Dark'
            
            # Save settings
            settings_window.save_settings()
            
            # Verify file was created
            assert config_file.exists()
            
            # Load settings in a new instance
            new_settings_window = SettingsWindow(
                parent=self.mock_parent,
                translate=self.mock_translate,
                load_translations_func=self.mock_load_translations,
                update_ui_texts_func=self.mock_update_ui_texts,
                save_language_preference_func=self.mock_save_language_preference,
                version="1.0.0",
                downloader=None,
                check_for_new_version_func=self.mock_check_for_new_version
            )
            
            loaded_settings = new_settings_window.load_settings()
            
            # Verify loaded values match saved values
            assert loaded_settings['max_downloads'] == 5
            assert loaded_settings['folder_structure'] == 'custom'
            assert loaded_settings['language'] == 'es'
            assert loaded_settings['theme'] == 'Dark'
        finally:
            SettingsWindow.CONFIG_PATH = original_path
    
    def test_save_creates_directory(self, tmp_path):
        """Test that save_settings creates directory if it doesn't exist."""
        config_file = tmp_path / "new_config_dir" / "settings.json"
        original_path = SettingsWindow.CONFIG_PATH
        SettingsWindow.CONFIG_PATH = str(config_file)
        
        try:
            settings_window = SettingsWindow(
                parent=self.mock_parent,
                translate=self.mock_translate,
                load_translations_func=self.mock_load_translations,
                update_ui_texts_func=self.mock_update_ui_texts,
                save_language_preference_func=self.mock_save_language_preference,
                version="1.0.0",
                downloader=None,
                check_for_new_version_func=self.mock_check_for_new_version
            )
            
            # Directory shouldn't exist yet
            assert not config_file.parent.exists()
            
            # Save settings
            settings_window.save_settings()
            
            # Directory and file should now exist
            assert config_file.parent.exists()
            assert config_file.exists()
        finally:
            SettingsWindow.CONFIG_PATH = original_path
    
    def test_load_corrupted_json_returns_defaults(self, tmp_path):
        """Test that corrupted JSON file returns default settings."""
        config_file = tmp_path / "settings.json"
        original_path = SettingsWindow.CONFIG_PATH
        SettingsWindow.CONFIG_PATH = str(config_file)
        
        try:
            # Create corrupted JSON file
            config_file.write_text("{ invalid json content }")
            
            settings_window = SettingsWindow(
                parent=self.mock_parent,
                translate=self.mock_translate,
                load_translations_func=self.mock_load_translations,
                update_ui_texts_func=self.mock_update_ui_texts,
                save_language_preference_func=self.mock_save_language_preference,
                version="1.0.0",
                downloader=None,
                check_for_new_version_func=self.mock_check_for_new_version
            )
            
            settings = settings_window.load_settings()
            
            # Should return defaults
            assert settings['max_downloads'] == 3
            assert settings['folder_structure'] == 'default'
        finally:
            SettingsWindow.CONFIG_PATH = original_path
    
    def test_settings_roundtrip_preserves_data(self, tmp_path):
        """Test that saving and loading preserves all data types correctly."""
        config_file = tmp_path / "settings.json"
        original_path = SettingsWindow.CONFIG_PATH
        SettingsWindow.CONFIG_PATH = str(config_file)
        
        try:
            settings_window = SettingsWindow(
                parent=self.mock_parent,
                translate=self.mock_translate,
                load_translations_func=self.mock_load_translations,
                update_ui_texts_func=self.mock_update_ui_texts,
                save_language_preference_func=self.mock_save_language_preference,
                version="1.0.0",
                downloader=None,
                check_for_new_version_func=self.mock_check_for_new_version
            )
            
            # Set various data types
            test_data = {
                'max_downloads': 10,
                'folder_structure': 'nested',
                'language': 'fr',
                'theme': 'Light',
                'custom_string': 'test_value',
                'custom_bool': True,
                'custom_number': 42.5
            }
            
            settings_window.settings = test_data
            settings_window.save_settings()
            
            # Read file directly and verify JSON structure
            with open(config_file, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data == test_data
            
            # Load through the class
            loaded_settings = settings_window.load_settings()
            
            # Verify all values and types are preserved
            assert loaded_settings['max_downloads'] == 10
            assert loaded_settings['folder_structure'] == 'nested'
            assert loaded_settings['language'] == 'fr'
            assert loaded_settings['theme'] == 'Light'
            assert loaded_settings['custom_string'] == 'test_value'
            assert loaded_settings['custom_bool'] is True
            assert loaded_settings['custom_number'] == 42.5
        finally:
            SettingsWindow.CONFIG_PATH = original_path
