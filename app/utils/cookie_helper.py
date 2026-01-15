"""
Cookie Helper - Automated cookie extraction from browsers.

Uses browser_cookie3 to extract cookies from Chrome, Firefox, Edge, etc.
"""
from __future__ import annotations

import json
from typing import List, Dict, Optional
from pathlib import Path


class CookieHelper:
    """Helper class for extracting and managing browser cookies."""
    
    SUPPORTED_BROWSERS = ['chrome', 'firefox', 'edge', 'opera', 'brave', 'chromium']
    
    def __init__(self):
        self.browser_cookie3 = None
        self._init_browser_cookie3()
    
    def _init_browser_cookie3(self):
        """Try to import browser_cookie3 module."""
        try:
            import browser_cookie3
            self.browser_cookie3 = browser_cookie3
        except ImportError:
            self.browser_cookie3 = None
    
    def is_available(self) -> bool:
        """Check if browser_cookie3 is available."""
        return self.browser_cookie3 is not None
    
    def extract_cookies(self, domain: str, browser: str = 'chrome') -> Optional[List[Dict]]:
        """
        Extract cookies from a specific browser for a domain.
        
        Args:
            domain: Domain to extract cookies for (e.g., 'simpcity.cr')
            browser: Browser name ('chrome', 'firefox', 'edge', etc.)
            
        Returns:
            List of cookie dictionaries, or None if extraction fails
        """
        if not self.is_available():
            return None
        
        try:
            browser = browser.lower()
            
            # Get the appropriate browser function
            if browser == 'chrome':
                cookie_jar = self.browser_cookie3.chrome(domain_name=domain)
            elif browser == 'firefox':
                cookie_jar = self.browser_cookie3.firefox(domain_name=domain)
            elif browser == 'edge':
                cookie_jar = self.browser_cookie3.edge(domain_name=domain)
            elif browser == 'opera':
                cookie_jar = self.browser_cookie3.opera(domain_name=domain)
            elif browser == 'brave':
                cookie_jar = self.browser_cookie3.brave(domain_name=domain)
            elif browser == 'chromium':
                cookie_jar = self.browser_cookie3.chromium(domain_name=domain)
            else:
                # Try chrome as default
                cookie_jar = self.browser_cookie3.chrome(domain_name=domain)
            
            # Convert cookie jar to our format
            return self.convert_to_json(cookie_jar)
            
        except Exception as e:
            # Common errors: browser not installed, browser running, permission denied
            return None
    
    def convert_to_json(self, cookie_jar) -> List[Dict]:
        """
        Convert cookie jar to JSON format expected by requests.
        
        Args:
            cookie_jar: Cookie jar object from browser_cookie3
            
        Returns:
            List of cookie dictionaries
        """
        cookies = []
        
        try:
            for cookie in cookie_jar:
                cookie_dict = {
                    'name': cookie.name,
                    'value': cookie.value,
                    'domain': cookie.domain,
                    'path': cookie.path,
                    'secure': cookie.secure,
                    'expires': cookie.expires if hasattr(cookie, 'expires') else None
                }
                cookies.append(cookie_dict)
        except Exception:
            pass
        
        return cookies
    
    def save_cookies(self, cookies: List[Dict], filepath: str) -> bool:
        """
        Save cookies to a JSON file.
        
        Args:
            cookies: List of cookie dictionaries
            filepath: Path to save the JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2)
            return True
        except Exception:
            return False
    
    def load_cookies(self, filepath: str) -> Optional[List[Dict]]:
        """
        Load cookies from a JSON file.
        
        Args:
            filepath: Path to the JSON file
            
        Returns:
            List of cookie dictionaries, or None if load fails
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    
    def get_manual_instructions(self, browser: str = 'chrome') -> str:
        """
        Generate step-by-step instructions for manual cookie export.
        
        Args:
            browser: Browser name
            
        Returns:
            Formatted instruction text
        """
        instructions = {
            'chrome': """
Manual Cookie Export for Chrome:

1. Open Chrome and navigate to the site (e.g., simpcity.cr)
2. Log in to your account
3. Right-click anywhere on the page → "Inspect" (or press F12)
4. Go to the "Application" tab (or "Storage" in some versions)
5. In the left sidebar, expand "Cookies"
6. Click on the site domain
7. Right-click on a cookie row → "Show Cookies"
8. Copy the cookie values you need:
   - Name: The cookie name
   - Value: The cookie value
   - Domain: The domain it belongs to
   
9. Create a JSON file with this format:
   [
     {
       "name": "session_id",
       "value": "your_session_value_here",
       "domain": ".simpcity.cr",
       "path": "/",
       "secure": true
     }
   ]

10. Save this file and import it using the "Load from File" button.

Alternative: Use a browser extension like "EditThisCookie" or "Cookie-Editor"
to export all cookies for the site as JSON.
            """,
            'firefox': """
Manual Cookie Export for Firefox:

1. Open Firefox and navigate to the site
2. Log in to your account
3. Right-click → "Inspect Element" (or press F12)
4. Go to the "Storage" tab
5. Expand "Cookies" in the left sidebar
6. Click on the site domain
7. You'll see all cookies listed
8. Copy the necessary cookie information
9. Create a JSON file with the format shown in Chrome instructions

Alternative: Use the "Cookie Quick Manager" extension for Firefox
to export cookies as JSON.
            """,
            'edge': """
Manual Cookie Export for Edge:

1. Open Edge and navigate to the site
2. Log in to your account
3. Right-click → "Inspect" (or press F12)
4. Go to the "Application" tab
5. Expand "Cookies" in the left sidebar
6. Follow the same steps as Chrome

Edge uses the same developer tools as Chrome.
            """
        }
        
        return instructions.get(browser.lower(), instructions['chrome'])
    
    def get_error_message(self, error: Exception) -> str:
        """
        Generate a user-friendly error message.
        
        Args:
            error: The exception that occurred
            
        Returns:
            User-friendly error message with suggestions
        """
        error_str = str(error).lower()
        
        if 'permission' in error_str or 'access denied' in error_str:
            return """
Permission Error: Cannot access browser cookies.

Solutions:
1. Close your browser completely before trying again
2. Run the application with appropriate permissions
3. Try a different browser
4. Use manual cookie export instead
            """
        
        elif 'not found' in error_str or 'no such file' in error_str:
            return """
Browser Not Found: The selected browser is not installed or cannot be located.

Solutions:
1. Select a different browser
2. Install the selected browser
3. Use manual cookie export instead
            """
        
        elif 'decode' in error_str or 'encrypt' in error_str:
            return """
Encryption Error: Cannot decrypt browser cookies.

Solutions:
1. Update browser_cookie3: pip install --upgrade browser_cookie3
2. Close the browser and try again
3. Use manual cookie export instead
            """
        
        else:
            return f"""
Unexpected Error: {error}

Solutions:
1. Try closing your browser and running again
2. Use a different browser
3. Use manual cookie export instead
4. Check if you have the latest version of browser_cookie3
            """
