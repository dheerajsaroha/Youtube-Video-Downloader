#!/usr/bin/env python3
"""
Simple test script to verify the downloader works
"""

import os
import sys

def test_imports():
    """Test if all required modules can be imported"""
    try:
        import yt_dlp
        print("✓ yt-dlp imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import yt-dlp: {e}")
        return False
    
    try:
        import tkinter
        print("✓ tkinter imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import tkinter: {e}")
        return False
    
    try:
        import threading
        import json
        from pathlib import Path
        print("✓ All standard library modules imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import standard library: {e}")
        return False
    
    return True

def test_yt_dlp_functionality():
    """Test if yt-dlp can extract basic video info"""
    try:
        import yt_dlp
        
        # Test with a short, safe video
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Astley
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(test_url, download=False)
            print(f"✓ Successfully extracted info: {info.get('title', 'Unknown')}")
            return True
            
    except Exception as e:
        print(f"✗ yt-dlp test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing YouTube Playlist Downloader...")
    print("=" * 50)
    
    if test_imports():
        print("\nTesting yt-dlp functionality...")
        test_yt_dlp_functionality()
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()
