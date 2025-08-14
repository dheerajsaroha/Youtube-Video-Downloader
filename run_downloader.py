#!/usr/bin/env python3
"""
Simple launcher script for the YouTube Playlist Downloader
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import yt_dlp
        print("✓ yt-dlp is installed")
    except ImportError:
        print("✗ yt-dlp not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
    
    try:
        import tkinter
        print("✓ tkinter is available")
    except ImportError:
        print("✗ tkinter not found. Please install python3-tk")
        return False
    
    return True

def main():
    """Main launcher function"""
    print("YouTube Playlist Downloader Launcher")
    print("=" * 40)
    
    if check_dependencies():
        print("\nAll dependencies satisfied!")
        print("Starting YouTube Playlist Downloader...")
        
        # Run the main application
        os.system(f"{sys.executable} youtube_downloader_fixed.py")
    else:
        print("\nPlease install missing dependencies and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
