"""
Tests for utility functions from app.ui module.
Tests URL parsing and extraction functions without modifying the source code.
"""
import pytest
import re
import sys
from urllib.parse import urlparse, ParseResult, parse_qs
from unittest.mock import MagicMock

# Mock all GUI-related modules before importing app.ui
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.scrolledtext'] = MagicMock()
sys.modules['customtkinter'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['PIL.ImageTk'] = MagicMock()
sys.modules['psutil'] = MagicMock()
sys.modules['tkinterweb'] = MagicMock()

from app.ui import extract_ck_parameters, extract_ck_query


class TestExtractCkParameters:
    """Test the extract_ck_parameters function that extracts service, user, and post from URLs."""
    
    def test_full_url_with_post(self):
        """Test extraction of service, user, and post from a complete URL."""
        url = urlparse("https://coomer.st/onlyfans/user/exampleuser/post/123456")
        service, user, post = extract_ck_parameters(url)
        
        assert service == "onlyfans"
        assert user == "exampleuser"
        assert post == "123456"
    
    def test_url_without_post(self):
        """Test extraction when URL has service and user but no post."""
        url = urlparse("https://coomer.st/patreon/user/testuser")
        service, user, post = extract_ck_parameters(url)
        
        assert service == "patreon"
        assert user == "testuser"
        assert post is None
    
    def test_url_with_trailing_slash(self):
        """Test extraction with trailing slash in URL."""
        url = urlparse("https://kemono.cr/fanbox/user/artist123/")
        service, user, post = extract_ck_parameters(url)
        
        assert service == "fanbox"
        assert user == "artist123"
        assert post is None
    
    def test_invalid_url_returns_none(self):
        """Test that URLs without user return None for user and post."""
        url = urlparse("https://coomer.st/invalid")
        service, user, post = extract_ck_parameters(url)
        
        # The function matches 'invalid' as service, but user and post should be None
        assert service == "invalid"
        assert user is None
        assert post is None
    
    def test_url_with_query_parameters(self):
        """Test extraction with query parameters in URL."""
        url = urlparse("https://coomer.st/subscribestar/user/creator/post/999?q=test&o=50")
        service, user, post = extract_ck_parameters(url)
        
        assert service == "subscribestar"
        assert user == "creator"
        assert post == "999"


class TestExtractCkQuery:
    """Test the extract_ck_query function that extracts query and offset parameters."""
    
    def test_both_query_and_offset(self):
        """Test extraction of both q and o parameters."""
        url = urlparse("https://coomer.st/onlyfans/user/test?q=search_term&o=100")
        query, offset = extract_ck_query(url)
        
        assert query == "search_term"
        assert offset == 100
    
    def test_query_only(self):
        """Test extraction when only q parameter exists."""
        url = urlparse("https://coomer.st/patreon/user/test?q=myquery")
        query, offset = extract_ck_query(url)
        
        assert query == "myquery"
        assert offset == 0
    
    def test_offset_only(self):
        """Test extraction when only o parameter exists."""
        url = urlparse("https://kemono.cr/fanbox/user/test?o=50")
        query, offset = extract_ck_query(url)
        
        assert query == "0"
        assert offset == 50
    
    def test_no_parameters(self):
        """Test default values when no query parameters exist."""
        url = urlparse("https://coomer.st/onlyfans/user/test")
        query, offset = extract_ck_query(url)
        
        assert query == "0"
        assert offset == 0
    
    def test_invalid_offset_returns_zero(self):
        """Test that non-numeric offset returns 0."""
        url = urlparse("https://coomer.st/test?o=invalid")
        query, offset = extract_ck_query(url)
        
        assert query == "0"
        assert offset == 0
    
    def test_empty_query_parameter(self):
        """Test handling of empty query parameter."""
        url = urlparse("https://coomer.st/test?q=&o=25")
        query, offset = extract_ck_query(url)
        
        assert query == "0"
        assert offset == 25
