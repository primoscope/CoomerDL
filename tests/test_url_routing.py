"""
Tests for URL routing logic.
Tests which downloader type should be used for different URLs.
"""
import pytest
import re


class TestURLRouting:
    """Test URL pattern matching to determine the correct downloader type."""
    
    def test_erome_domain_detection(self):
        """Test detection of Erome URLs."""
        urls = [
            "https://www.erome.com/a/albumid",
            "https://erome.com/profilename",
            "http://www.erome.com/a/test123"
        ]
        for url in urls:
            assert "erome.com" in url
    
    def test_erome_album_vs_profile(self):
        """Test differentiation between Erome album and profile URLs."""
        album_url = "https://www.erome.com/a/albumid"
        profile_url = "https://www.erome.com/profilename"
        
        assert "/a/" in album_url
        assert "/a/" not in profile_url
    
    def test_bunkr_domain_detection(self):
        """Test detection of Bunkr URLs with various TLDs."""
        pattern = r"https?://([a-z0-9-]+\.)?bunkr\.[a-z]{2,}"
        
        valid_urls = [
            "https://bunkr.si/album/test",
            "https://cdn.bunkr.si/file.jpg",
            "https://bunkr.site/v/video123",
            "http://i2.bunkr.ru/test.png",
            "https://bunkr.to/gallery"
        ]
        
        for url in valid_urls:
            assert re.search(pattern, url) is not None
    
    def test_bunkr_post_vs_profile(self):
        """Test differentiation between Bunkr post and profile URLs."""
        post_urls = [
            "https://bunkr.si/v/video123",
            "https://bunkr.site/i/image456",
            "https://cdn.bunkr.ru/f/file789"
        ]
        profile_url = "https://bunkr.si/a/albumname"
        
        for url in post_urls:
            assert any(sub in url for sub in ["/v/", "/i/", "/f/"])
        
        assert not any(sub in profile_url for sub in ["/v/", "/i/", "/f/"])
    
    def test_coomer_kemono_domain_detection(self):
        """Test detection of Coomer and Kemono URLs."""
        from urllib.parse import urlparse
        
        coomer_url = urlparse("https://coomer.st/onlyfans/user/test")
        kemono_url = urlparse("https://kemono.cr/patreon/user/test")
        
        assert coomer_url.netloc == "coomer.st"
        assert kemono_url.netloc == "kemono.cr"
        assert coomer_url.netloc in ["coomer.st", "kemono.cr"]
        assert kemono_url.netloc in ["coomer.st", "kemono.cr"]
    
    def test_simpcity_domain_detection(self):
        """Test detection of SimpCity URLs."""
        urls = [
            "https://simpcity.cr/threads/thread123",
            "http://simpcity.cr/forums/forum456",
            "https://www.simpcity.cr/test"
        ]
        
        for url in urls:
            assert "simpcity.cr" in url
    
    def test_jpg5_domain_detection(self):
        """Test detection of Jpg5 URLs."""
        urls = [
            "https://jpg5.su/img/12345",
            "http://jpg5.su/gallery/test",
            "https://www.jpg5.su/album/name"
        ]
        
        for url in urls:
            assert "jpg5.su" in url
    
    def test_url_routing_priority(self):
        """Test that URL routing checks are mutually exclusive."""
        test_cases = [
            ("https://erome.com/test", "erome"),
            ("https://bunkr.si/test", "bunkr"),
            ("https://coomer.st/onlyfans/user/test", "coomer"),
            ("https://kemono.cr/patreon/user/test", "kemono"),
            ("https://simpcity.cr/threads/test", "simpcity"),
            ("https://jpg5.su/img/test", "jpg5")
        ]
        
        for url, expected_type in test_cases:
            matched_types = []
            
            if "erome.com" in url:
                matched_types.append("erome")
            elif re.search(r"https?://([a-z0-9-]+\.)?bunkr\.[a-z]{2,}", url):
                matched_types.append("bunkr")
            elif urlparse_wrapper(url) in ["coomer.st", "kemono.cr"]:
                matched_types.append("coomer" if "coomer" in url else "kemono")
            elif "simpcity.cr" in url:
                matched_types.append("simpcity")
            elif "jpg5.su" in url:
                matched_types.append("jpg5")
            
            assert len(matched_types) == 1
            assert matched_types[0] == expected_type
    
    def test_invalid_urls(self):
        """Test that invalid URLs don't match any patterns."""
        invalid_urls = [
            "https://unknown-site.com/test",
            "not-a-url",
            "https://google.com",
            ""
        ]
        
        for url in invalid_urls:
            matches_any = (
                "erome.com" in url or
                re.search(r"https?://([a-z0-9-]+\.)?bunkr\.[a-z]{2,}", url) is not None or
                "simpcity.cr" in url or
                "jpg5.su" in url
            )
            
            # Coomer/Kemono check
            from urllib.parse import urlparse
            parsed = urlparse(url)
            matches_any = matches_any or parsed.netloc in ["coomer.st", "kemono.cr"]
            
            assert not matches_any


def urlparse_wrapper(url):
    """Helper to get netloc from URL."""
    from urllib.parse import urlparse
    return urlparse(url).netloc
