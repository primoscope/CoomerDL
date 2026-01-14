import os
import sys

def run_headless_server():
    """
    Runs a simple HTTP server to keep the Render deployment alive
    and inform the user that this is a Desktop app.
    """
    import http.server
    import socketserver

    # Render provides the PORT environment variable
    PORT = int(os.environ.get("PORT", 8080))

    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>CoomerDL - Desktop Application</title>
                <style>
                    body { font-family: sans-serif; text-align: center; padding: 50px; background-color: #1a1a1a; color: #f0f0f0; }
                    h1 { color: #4CAF50; }
                    .container { max-width: 600px; margin: 0 auto; background: #2d2d2d; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
                    a { color: #64B5F6; text-decoration: none; }
                    a:hover { text-decoration: underline; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>CoomerDL is running!</h1>
                    <p>However, this is a <strong>Desktop Application</strong> (GUI), so you cannot interact with it through this web browser.</p>
                    <p>The application has started in <strong>Headless Mode</strong> to prevent deployment failure.</p>
                    <hr style="border-color: #444;">
                    <p>To use CoomerDL, please download the source code and run it on your local machine:</p>
                    <p><a href="https://github.com/primoscope/CoomerDL">View on GitHub</a></p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode('utf-8'))

    print(f"Starting headless info server on port {PORT}...")
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Serving at port {PORT}")
            httpd.serve_forever()
    except Exception as e:
        print(f"Failed to start headless server: {e}")

def main():
    # 1. Check for Tkinter availability
    tkinter_available = False
    try:
        import tkinter
        tkinter_available = True
    except ImportError:
        print("Warning: Tkinter not found. GUI cannot start.")

    # 2. Check for Headless/Render environment
    # Render sets 'RENDER' to 'true'
    is_render = os.environ.get("RENDER") == "true"
    is_headless = os.environ.get("HEADLESS") == "true" or not tkinter_available

    if is_render or is_headless:
        print("Detected Headless/Render environment.")
        print("Starting placeholder web server...")
        run_headless_server()
        return

    # 3. Start Desktop GUI
    try:
        # Import here to avoid top-level ImportError in headless envs
        from app.sidebar_app import SidebarApp
        app = SidebarApp()
        app.mainloop()
    except Exception as e:
        print(f"Critical Error starting GUI: {e}")
        # Fallback to headless server if GUI crashes immediately (e.g. no DISPLAY)
        print("Falling back to headless server...")
        run_headless_server()

if __name__ == "__main__":
    main()
