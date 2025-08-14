#!/usr/bin/env python3
"""
YouTube Playlist Downloader with GUI
A modern GUI application for downloading YouTube playlists with quality selection
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp
import os
import threading
from typing import Optional, Dict, Any
import json
from pathlib import Path

class YouTubeDownloader:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("YouTube Playlist Downloader")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Configuration
        self.config_file = "downloader_config.json"
        self.download_path = str(Path.home() / "Downloads")
        self.current_download = None
        self.is_downloading = False
        
        # Load saved configuration
        self.load_config()
        
        # Setup GUI
        self.setup_gui()
        
    def load_config(self):
        """Load saved configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.download_path = config.get('download_path', self.download_path)
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            config = {
                'download_path': self.download_path
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def setup_gui(self):
        """Setup the main GUI interface"""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # URL Input Section
        url_label = ttk.Label(main_frame, text="Playlist URL:")
        url_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.url_entry = ttk.Entry(main_frame, width=50)
        self.url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Download Path Section
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        path_label = ttk.Label(path_frame, text="Download Path:")
        path_label.grid(row=0, column=0, sticky=tk.W)
        
        self.path_entry = ttk.Entry(path_frame, width=40)
        self.path_entry.insert(0, self.download_path)
        self.path_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        
        browse_btn = ttk.Button(path_frame, text="Browse", command=self.browse_path)
        browse_btn.grid(row=0, column=2)
        
        path_frame.columnconfigure(1, weight=1)
        
        # Quality Selection Section
        quality_frame = ttk.LabelFrame(main_frame, text="Quality Selection", padding="5")
        quality_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.quality_var = tk.StringVar(value="best")
        qualities = [
            ("Best Quality", "best"),
            ("1080p", "best[height<=1080]"),
            ("720p", "best[height<=720]"),
            ("480p", "best[height<=480]"),
            ("360p", "best[height<=360]"),
            ("Audio Only", "bestaudio")
        ]
        
        for i, (text, value) in enumerate(qualities):
            rb = ttk.Radiobutton(quality_frame, text=text, value=value, variable=self.quality_var)
            rb.grid(row=i//2, column=i%2, sticky=tk.W, padx=5, pady=2)
        
        # Format Selection
        format_frame = ttk.LabelFrame(main_frame, text="Format Options", padding="5")
        format_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.format_var = tk.StringVar(value="mp4")
        formats = [("MP4", "mp4"), ("MKV", "mkv"), ("WebM", "webm"), ("MP3", "mp3")]
        
        for i, (text, value) in enumerate(formats):
            rb = ttk.Radiobutton(format_frame, text=text, value=value, variable=self.format_var)
            rb.grid(row=0, column=i, sticky=tk.W, padx=5)
        
        # Buttons Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(0, 10))
        
        self.download_btn = ttk.Button(button_frame, text="Download Playlist", command=self.start_download)
        self.download_btn.grid(row=0, column=0, padx=5)
        
        self.cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.cancel_download, state=tk.DISABLED)
        self.cancel_btn.grid(row=0, column=1, padx=5)
        
        # Progress Section
        progress_frame = ttk.LabelFrame(main_frame, text="Download Progress", padding="5")
        progress_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.progress_label = ttk.Label(progress_frame, text="Ready to download")
        self.progress_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=300)
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 5))
        
        self.progress_text = tk.Text(progress_frame, height=8, width=60)
        self.progress_text.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        
        # Scrollbar for progress text
        scrollbar = ttk.Scrollbar(progress_frame, orient="vertical", command=self.progress_text.yview)
        scrollbar.grid(row=2, column=1, sticky=(tk.N, tk.S))
        self.progress_text.configure(yscrollcommand=scrollbar.set)
        
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(2, weight=1)
        
        # Configure main frame weights
        main_frame.rowconfigure(5, weight=1)
    
    def browse_path(self):
        """Open folder browser to select download path"""
        path = filedialog.askdirectory(initialdir=self.download_path)
        if path:
            self.download_path = path
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)
            self.save_config()
    
    def start_download(self):
        """Start the download process in a separate thread"""
        if self.is_downloading:
            return
            
        url = self.url_entry.get().strip()
        if not url:
The `requirements.txt` file has been created successfully. Now, I will proceed to create the main application file `youtube_downloader.py`.

<create_file>
<path>youtube_downloader.py</path>
<content>
#!/usr/bin/env python3
"""
YouTube Playlist Downloader with GUI
A modern GUI application for downloading YouTube playlists with quality selection
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp
import os
import threading
from typing import Optional, Dict, Any
import json
from pathlib import Path

class YouTubeDownloader:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("YouTube Playlist Downloader")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Configuration
        self.config_file = "downloader_config.json"
        self.download_path = str(Path.home() / "Downloads")
        self.current_download = None
        self.is_downloading = False
        
        # Load saved configuration
        self.load_config()
        
        # Setup GUI
        self.setup_gui()

    def load_config(self):
        """Load configuration from a JSON file."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.download_path = config.get("download_path", self.download_path)

    def save_config(self):
        """Save configuration to a JSON file."""
        config = {"download_path": self.download_path}
        with open(self.config_file, 'w') as f:
            json.dump(config, f)

    def setup_gui(self):
        """Setup the GUI components."""
        # URL Entry
        self.url_label = ttk.Label(self.root, text="YouTube Playlist URL:")
        self.url_label.pack(pady=10)
        self.url_entry = ttk.Entry(self.root, width=50)
        self.url_entry.pack(pady=10)

        # Quality Selection
        self.quality_label = ttk.Label(self.root, text="Select Video Quality:")
        self.quality_label.pack(pady=10)
        self.quality_var = tk.StringVar(value="best")
        self.quality_combobox = ttk.Combobox(self.root, textvariable=self.quality_var, values=["best", "worst", "720p", "480p", "360p"])
        self.quality_combobox.pack(pady=10)

        # Download Path
        self.path_label = ttk.Label(self.root, text="Download Path:")
        self.path_label.pack(pady=10)
        self.path_entry = ttk.Entry(self.root, width=50)
        self.path_entry.pack(pady=10)
        self.path_entry.insert(0, self.download_path)
        self.browse_button = ttk.Button(self.root, text="Browse", command=self.browse_path)
        self.browse_button.pack(pady=10)

        # Download Button
        self.download_button = ttk.Button(self.root, text="Download Playlist", command=self.start_download)
        self.download_button.pack(pady=20)

        # Status Label
        self.status_label = ttk.Label(self.root, text="")
        self.status_label.pack(pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def browse_path(self):
        """Open a file dialog to select download path."""
        path = filedialog.askdirectory()
        if path:
            self.download_path = path
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, self.download_path)

    def start_download(self):
        """Start the download process in a separate thread."""
        if self.is_downloading:
            messagebox.showwarning("Warning", "A download is already in progress.")
            return
        self.is_downloading = True
        self.current_download = threading.Thread(target=self.download_playlist)
        self.current_download.start()

    def download_playlist(self):
        """Download the playlist using yt-dlp."""
        url = self.url_entry.get()
        quality = self.quality_var.get()
        self.save_config()
        self.status_label.config(text="Downloading...")

        ydl_opts = {
            'format': quality,
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
            'noplaylist': False,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.status_label.config(text="Download completed!")
        except Exception as e:
            self.status_label.config(text="Error occurred!")
            messagebox.showerror("Error", str(e))
        finally:
            self.is_downloading = False

    def on_closing(self):
        """Handle window closing event."""
        self.save_config()
        self.root.destroy()

if __name__ == "__main__":
    YouTubeDownloader()
