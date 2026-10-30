"""Desktop Application Launcher for Motorsport Strategy Optimizer.

Runs the FastAPI backend and embeds the React dashboard in a native desktop window.
"""

import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

import uvicorn

# Resolve root directory whether running as python script or frozen exe
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    ROOT_DIR = Path(sys._MEIPASS)
else:
    ROOT_DIR = Path(__file__).resolve().parent

sys.path.insert(0, str(ROOT_DIR))

from app.main import app


def find_available_port(default_port: int = 8000) -> int:
    """Check if default_port is free, otherwise select an ephemeral open port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(("127.0.0.1", default_port)) != 0:
            return default_port
    # If 8000 is occupied, pick a free port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def start_server(host: str, port: int) -> None:
    """Run uvicorn server programmatically."""
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level="warning",
        access_log=False,
    )
    server = uvicorn.Server(config)
    server.run()


def wait_for_server(url: str, timeout: float = 10.0) -> bool:
    """Wait until the HTTP server is responsive."""
    import urllib.request

    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(f"{url}/health", timeout=1.0) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.15)
    return False


def main():
    port = find_available_port(8000)
    host = "127.0.0.1"
    url = f"http://{host}:{port}"

    # Launch backend server thread
    server_thread = threading.Thread(target=start_server, args=(host, port), daemon=True)
    server_thread.start()

    # Wait for server to become responsive
    wait_for_server(url)

    # Try PyWebView native desktop window first
    use_webview = True
    try:
        import webview

        window = webview.create_window(
            title="Motorsport Pit-Stop & Tire Strategy Optimizer",
            url=url,
            width=1536,
            height=960,
            min_size=(1100, 700),
            background_color="#090D12",
        )
        webview.start()
    except Exception as exc:
        print(f"Native webview unavailable ({exc}), launching default browser...")
        use_webview = False

    if not use_webview:
        webbrowser.open(url)
        print("=" * 70)
        print("  MOTORSPORT STRATEGY OPTIMIZER DESKTOP APP IS ACTIVE")
        print(f"  Dashboard: {url}")
        print("  Press Ctrl+C to terminate application.")
        print("=" * 70)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down desktop app...")


if __name__ == "__main__":
    main()
