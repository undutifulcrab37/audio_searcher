#!/usr/bin/env python3
import os
import sys
import subprocess
import webbrowser
import time
import threading
import signal

def open_browser():
    # Wait a moment for the server to start
    time.sleep(3)
    # Open browser at the streamlit local URL
    webbrowser.open("http://localhost:8501")

def cleanup(signum, frame):
    # Handle cleanup when the app is closed
    print("Exiting AUCHIVE application...")
    sys.exit(0)

def main():
    # Register signal handlers for clean exit
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    # Determine the app path
    if getattr(sys, 'frozen', False):
        # Running as a bundled application
        app_path = os.path.join(os.path.dirname(sys.executable), 'Resources')
    else:
        # Running in a normal Python environment
        app_path = os.path.dirname(os.path.abspath(__file__))
    
    # Create cache directories if they don't exist
    os.makedirs(os.path.join(app_path, "data", "audio_cache"), exist_ok=True)
    os.makedirs(os.path.join(app_path, "data", "transcript_cache"), exist_ok=True)
    
    # Change directory to the app path
    os.chdir(app_path)
    
    # Start thread to open browser
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start streamlit
    try:
        import streamlit.web.cli as stcli
        sys.argv = ["streamlit", "run", "app.py", "--server.headless", "true", "--browser.serverAddress", "localhost"]
        stcli.main()
    except Exception as e:
        print(f"Error starting AUCHIVE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
