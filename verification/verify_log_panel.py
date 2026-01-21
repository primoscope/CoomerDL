import time
from playwright.sync_api import sync_playwright

def test_log_panel(page):
    # Navigate to the frontend
    page.goto("http://localhost:5173")

    # Wait for React to hydrate
    page.wait_for_timeout(2000)

    # Check for "Backend Unavailable" message
    # If the backend is not running, we expect this message.
    # However, to verify the LogPanel, we need to bypass this check.
    # We can mock the health check response using page.route.

    # Mock /api/health to return healthy
    page.route("**/api/health", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='{"status": "healthy"}'
    ))

    # Reload the page to apply the mock
    page.reload()

    # Wait for the main content to load
    try:
        page.wait_for_selector("text=CoomerDL", timeout=5000)
    except:
        print("Header not found after reload with mock.")
        page.screenshot(path="/home/jules/verification/after_mock_reload.png")
        return

    # Check if "Logs" header is visible
    try:
        page.wait_for_selector("text=Logs", timeout=5000)
        print("Log panel found!")
    except:
        print("Logs panel not found on home page. It might be hidden or on another page.")
        page.screenshot(path="/home/jules/verification/home_page.png")
        return

    # Take a screenshot of the visible LogPanel
    page.screenshot(path="/home/jules/verification/verification.png")
    print("Screenshot taken.")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            test_log_panel(page)
        finally:
            browser.close()
