from typing import List, Optional
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from urllib.parse import urlparse
import re

@dataclass
class BatchMetadata:
    url: str
    count_images: int = 0
    count_videos: int = 0
    count_others: int = 0
    total_est_size_mb: float = 0.0
    title: str = "Unknown"
    is_supported: bool = True

class BatchLinkAnalyzer:
    """
    Helper class to analyze links before downloading.
    It can be used to show a preview of what will be downloaded.
    """

    def __init__(self, user_agent: str = None):
        self.headers = {
            'User-Agent': user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def analyze(self, url: str) -> BatchMetadata:
        """
        Analyze a URL and return metadata about potential downloads.
        This is a 'best effort' implementation that might not be 100% accurate for all sites.
        """
        meta = BatchMetadata(url=url)

        try:
            # Simple heuristic based on domain
            domain = urlparse(url).netloc.lower()

            if "coomer" in domain or "kemono" in domain:
                return self._analyze_coomer_kemono(url, meta)
            elif "erome" in domain:
                return self._analyze_erome(url, meta)
            elif "bunkr" in domain:
                return self._analyze_bunkr(url, meta)
            # Add more specific analyzers here

            # Fallback to generic analysis
            return self._analyze_generic(url, meta)

        except Exception as e:
            # If analysis fails, return what we have with is_supported=False or partial data
            print(f"Analysis failed for {url}: {e}")
            return meta

    def _analyze_coomer_kemono(self, url: str, meta: BatchMetadata) -> BatchMetadata:
        # Example logic for coomer/kemono
        # In a real scenario, this would likely query their API: /api/v1/user/{id}/posts
        # For now, let's try a simple scrape or API call if structure is known

        # Detect if it's a user profile or a single post
        if "/user/" in url:
            # Profile: try to fetch the first page or API to get stats
            # This is complex without full API implementation,
            # so we might return a "Placeholder" or try to parse the page title
            try:
                # Attempt to get page title
                resp = requests.get(url, headers=self.headers, timeout=10)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.content, 'html.parser')
                    title = soup.title.string if soup.title else "Profile"
                    meta.title = title.strip()

                    # Try to find "Displaying X of Y posts"
                    # <small>Displaying 1 - 50 of 1337 posts</small>
                    small_text = soup.find('small')
                    if small_text and "posts" in small_text.text:
                        # Extract total posts
                        match = re.search(r'of\s+(\d+)\s+posts', small_text.text)
                        if match:
                            total_posts = int(match.group(1))
                            # Rough estimate: 5 files per post?
                            meta.count_images = total_posts * 5 # Very rough
                            meta.total_est_size_mb = total_posts * 5 * 2 # 2MB per image?
            except:
                pass
        return meta

    def _analyze_erome(self, url: str, meta: BatchMetadata) -> BatchMetadata:
        # Erome album pages usually show count explicitly
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, 'html.parser')
                meta.title = soup.title.string.strip() if soup.title else "Erome Album"

                # Count videos and images
                videos = soup.find_all('video')
                images = soup.find_all('img', class_='img-front') # class might vary

                meta.count_videos = len(videos)
                # Erome lazy loads, so this is just visible ones.
                # Often the count is in the text like "12 Videos, 45 Images"

        except:
            pass
        return meta

    def _analyze_bunkr(self, url: str, meta: BatchMetadata) -> BatchMetadata:
        # Bunkr albums
        return meta

    def _analyze_generic(self, url: str, meta: BatchMetadata) -> BatchMetadata:
        # Generic fallback
        meta.is_supported = True # Assume supported via generic downloader
        return meta
