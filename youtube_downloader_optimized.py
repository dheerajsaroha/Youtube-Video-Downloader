#!/usr/bin/env python3
"""
Optimized YouTube Playlist Downloader with Fast Analysis
Enhanced performance for playlist analysis and download management
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp
import os
import threading
import json
from pathlib import Path
import time
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import queue


class VideoItem:
    """Represents an individual video in a playlist"""
    def __init__(self, video_id, title, url, duration=None, thumbnail=None):
        self.id = video_id
        self.title = title
        self.url = url
        self.duration = duration
        self.thumbnail = thumbnail
        
        # Download status
        self.progress = 0
        self.status = "pending"  # pending, downloading, paused, completed, failed
        self.speed = ""
        self.eta = ""
        self.filesize = 0
        self.downloaded_bytes = 0
        self.error_message = ""
        self.output_filename = ""
        
        # Thread control
        self.download_thread = None
        self.is_paused = False
        self.is_cancelled = False


class YouTubeDownloaderOptimized:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Optimized YouTube Playlist Downloader")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Configuration
        self.config_file = "downloader_config.json"
        self.download_path = str(Path.home() / "Downloads")
        self.videos = []  # List of VideoItem objects
        self.current_download = None
        self.analysis_thread = None
        
        # Load saved configuration
        self.load_config()
        
        # Setup GUI
        self.setup_gui()
        self.root.mainloop()
    
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
            config = {'download_path': self.download_path}
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def setup_gui(self):
        """Setup the optimized GUI interface"""
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
        
        analyze_btn = ttk.Button(main_frame, text="Analyze Playlist", command=self.analyze_playlist)
        analyze_btn.grid(row=0, column=2, padx=(5, 0))
        
        # Progress bar for analysis
        self.analysis_progress = ttk.Progressbar(main_frame, mode='indeterminate', length=200)
        self.analysis_progress.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 10))
        self.analysis_progress.grid_remove()  # Initially hidden
        
        # Download Path Section
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        path_label = ttk.Label(path_frame, text="Download Path:")
        path_label.grid(row=0, column=0, sticky=tk.W)
        
        self.path_entry = ttk.Entry(path_frame, width=40)
        self.path_entry.insert(0, self.download_path)
        self.path_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        
        browse_btn = ttk.Button(path_frame, text="Browse", command=self.browse_path)
        browse_btn.grid(row=0, column=2)
        
        path_frame.columnconfigure(1, weight=1)
        
        # Settings Frame
        settings_frame = ttk.LabelFrame(main_frame, text="Download Settings", padding="5")
        settings_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Quality Selection
        quality_label = ttk.Label(settings_frame, text="Quality:")
        quality_label.grid(row=0, column=0, sticky=tk.W)
        
        self.quality_var = tk.StringVar(value="best")
        quality_combo = ttk.Combobox(settings_frame, textvariable=self.quality_var, 
                                     values=["best", "1080p", "720p", "480p", "360p", "audio_only"], 
                                     width=15, state="readonly")
        quality_combo.grid(row=0, column=1, padx=(5, 20))
        
        # Format Selection
        format_label = ttk.Label(settings_frame, text="Format:")
        format_label.grid(row=0, column=2, sticky=tk.W)
        
        self.format_var = tk.StringVar(value="mp4")
        format_combo = ttk.Combobox(settings_frame, textvariable=self.format_var, 
                                   values=["mp4", "mkv", "webm", "mp3"], 
                                   width=10, state="readonly")
        format_combo.grid(row=0, column=3, padx=(5, 20))
        
        # Fast Analysis Option
        self.fast_analysis_var = tk.BooleanVar(value=True)
        fast_analysis_check = ttk.Checkbutton(settings_frame, text="Fast Analysis", 
                                            variable=self.fast_analysis_var)
        fast_analysis_check.grid(row=0, column=4, padx=(20, 5))
        
        # Download All Button
        self.download_all_btn = ttk.Button(settings_frame, text="Download All", command=self.download_all_videos, state=tk.DISABLED)
        self.download_all_btn.grid(row=0, column=5, padx=(20, 5))
        
        # Videos List Section
        videos_frame = ttk.LabelFrame(main_frame, text="Videos", padding="5")
        videos_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Create Treeview for videos
        columns = ('title', 'duration', 'progress', 'speed', 'eta', 'status', 'actions')
        self.videos_tree = ttk.Treeview(videos_frame, columns=columns, show='tree headings', height=15)
        
        # Configure columns
        self.videos_tree.heading('#0', text='#')
        self.videos_tree.column('#0', width=30, stretch=False)
        
        column_configs = {
            'title': {'heading': 'Title', 'width': 300},
            'duration': {'heading': 'Duration', 'width': 80},
            'progress': {'heading': 'Progress', 'width': 150},
            'speed': {'heading': 'Speed', 'width': 100},
            'eta': {'heading': 'ETA', 'width': 80},
            'status': {'heading': 'Status', 'width': 100},
            'actions': {'heading': 'Actions', 'width': 150}
        }
        
        for col, config in column_configs.items():
            self.videos_tree.heading(col, text=config['heading'])
            self.videos_tree.column(col, width=config['width'])
        
        # Add scrollbars
        vsb = ttk.Scrollbar(videos_frame, orient="vertical", command=self.videos_tree.yview)
        hsb = ttk.Scrollbar(videos_frame, orient="horizontal", command=self.videos_tree.xview)
        self.videos_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.videos_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        videos_frame.columnconfigure(0, weight=1)
        videos_frame.rowconfigure(0, weight=1)
        
        # Overall Progress
        overall_frame = ttk.Frame(main_frame)
        overall_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.overall_label = ttk.Label(overall_frame, text="Overall Progress: Ready")
        self.overall_label.grid(row=0, column=0, sticky=tk.W)
        
        self.overall_progress = ttk.Progressbar(overall_frame, mode='determinate', length=400)
        self.overall_progress.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Control Buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=6, column=0, columnspan=3, pady=(0, 10))
        
        self.pause_all_btn = ttk.Button(control_frame, text="Pause All", command=self.pause_all_downloads, state=tk.DISABLED)
        self.pause_all_btn.grid(row=0, column=0, padx=5)
        
        self.resume_all_btn = ttk.Button(control_frame, text="Resume All", command=self.resume_all_downloads, state=tk.DISABLED)
        self.resume_all_btn.grid(row=0, column=1, padx=5)
        
        self.cancel_all_btn = ttk.Button(control_frame, text="Cancel All", command=self.cancel_all_downloads, state=tk.DISABLED)
        self.cancel_all_btn.grid(row=0, column=2, padx=5)
        
        # Configure main frame weights
        main_frame.rowconfigure(4, weight=1)
        
        # Bind double-click to play/pause
        self.videos_tree.bind('<Double-1>', self.on_video_double_click)
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def browse_path(self):
        """Open folder browser to select download path"""
        path = filedialog.askdirectory(initialdir=self.download_path)
        if path:
            self.download_path = path
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)
            self.save_config()
    
    def analyze_playlist(self):
        """Analyze playlist with optimized performance"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube playlist URL")
            return
            
        # Disable analyze button and show progress
        self.analysis_progress.grid()
        self.analysis_progress.start()
        
        # Start analysis in separate thread
        self.analysis_thread = threading.Thread(target=self._analyze_playlist_thread, args=(url,))
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
    
    def _analyze_playlist_thread(self, url):
        """Thread function for playlist analysis with optimizations"""
        try:
            self.log_message("Analyzing playlist...")
            
            # Optimized yt-dlp options for faster analysis
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': 'in_playlist',  # Faster: don't extract full info initially
                'skip_download': True,
                'playlistend': 1000,  # Limit to prevent excessive loading
                'ignoreerrors': True,
            }
            
            # Use fast analysis mode if enabled
            if self.fast_analysis_var.get():
                ydl_opts.update({
                    'extract_flat': True,  # Much faster: only get basic info
                    'playlistend': 500,    # Limit playlist size for speed
                })
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                self.videos.clear()
                
                # Process results in main thread
                self.root.after(0, lambda: self._process_analysis_results(info))
                
        except Exception as e:
            self.root.after(0, lambda: self._handle_analysis_error(str(e)))
    
    def _process_analysis_results(self, info):
        """Process analysis results in main thread"""
        try:
            self.videos_tree.delete(*self.videos_tree.get_children())
            self.videos.clear()
            
            if info.get('_type') == 'playlist':
                playlist_title = info.get('title', 'Unknown Playlist')
                videos = info['entries']
                
                # Process videos efficiently
                video_list = []
                for idx, video in enumerate(videos, 1):
                    if video and video.get('id'):
                        video_item = VideoItem(
                            video_id=video.get('id', str(idx)),
                            title=video.get('title', f'Video {idx}'),
                            url=f"https://www.youtube.com/watch?v={video.get('id', '')}",
                            duration=video.get('duration_string', 'Unknown'),
                            thumbnail=video.get('thumbnail')
                        )
                        video_list.append(video_item)
                
                self.videos.extend(video_list)
                
                # Batch insert into treeview for better performance
                for idx, video_item in enumerate(video_list, 1):
                    self.videos_tree.insert('', 'end', iid=video_item.id, text=str(idx),
                                          values=(video_item.title, video_item.duration, 
                                                 f"{video_item.progress}%", video_item.speed,
                                                 video_item.eta, video_item.status, ''))
                
                self.log_message(f"Found {len(self.videos)} videos in playlist: {playlist_title}")
                
            else:
                # Single video
                video_item = VideoItem(
                    video_id=info.get('id', '1'),
                    title=info.get('title', 'Single Video'),
                    url=info.get('webpage_url', ''),
                    duration=info.get('duration_string', 'Unknown'),
                    thumbnail=info.get('thumbnail')
                )
                self.videos.append(video_item)
                
                self.videos_tree.insert('', 'end', iid=video_item.id, text='1',
                                      values=(video_item.title, video_item.duration, 
                                             f"{video_item.progress}%", video_item.speed,
                                             video_item.eta, video_item.status, ''))
                
                self.log_message("Found single video")
            
            self.download_all_btn.config(state=tk.NORMAL)
            
        finally:
            # Hide progress bar
            self.analysis_progress.stop()
            self.analysis_progress.grid_remove()
    
    def _handle_analysis_error(self, error_msg):
        """Handle analysis errors"""
        messagebox.showerror("Error", f"Failed to analyze playlist: {error_msg}")
        self.log_message(f"Error analyzing playlist: {error_msg}")
        self.analysis_progress.stop()
        self.analysis_progress.grid_remove()
    
    def download_all_videos(self):
        """Download all videos in the list"""
        if not self.videos:
            messagebox.showwarning("Warning", "No videos to download")
            return
            
        self.pause_all_btn.config(state=tk.NORMAL)
        self.cancel_all_btn.config(state=tk.NORMAL)
        
        # Start download thread
        download_thread = threading.Thread(target=self._download_all_videos_thread)
        download_thread.daemon = True
        download_thread.start()
    
    def _download_all_videos_thread(self):
        """Thread function to download all videos"""
        total_videos = len(self.videos)
        completed = 0
        
        for video in self.videos:
            if video.status in ['completed', 'failed']:
                continue
                
            self.root.after(0, lambda: self.overall_label.config(text=f"Downloading {completed+1}/{total_videos}: {video.title}"))
            
            self.download_single_video(video)
            
            if video.status == 'completed':
                completed += 1
                progress = (completed / total_videos) * 100
                self.root.after(0, lambda p=progress: self.overall_progress.config(value=p))
        
        self.root.after(0, lambda: self.overall_label.config(text=f"Download completed: {completed}/{total_videos} videos"))
        self.root.after(0, lambda: self.pause_all_btn.config(state=tk.DISABLED))
        self.root.after(0, lambda: self.cancel_all_btn.config(state=tk.DISABLED))
    
    def download_single_video(self, video_item):
        """Download a single video"""
        try:
            video_item.status = "downloading"
            video_item.is_cancelled = False
            video_item.is_paused = False
            
            quality = self.quality_var.get()
            output_format = self.format_var.get()
            
            ydl_opts = {
                'format': quality,
                'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                'noplaylist': True,
                'ignoreerrors': False,
                'no_warnings': False,
                'progress_hooks': [lambda d: self.video_progress_hook(d, video_item)],
            }
            
            if output_format != 'mp3':
                ydl_opts['merge_output_format'] = output_format
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_item.url])
                
        except Exception as e:
            video_item.status = "failed"
            video_item.error_message = str(e)
            self.log_message(f"Error downloading {video_item.title}: {str(e)}")
    
    def video_progress_hook(self, d, video_item):
        """Handle progress updates for individual videos"""
        if video_item.is_cancelled:
            raise Exception("Download cancelled")
            
        while video_item.is_paused:
            time.sleep(0.1)
            
        if d['status'] == 'downloading':
            video_item.downloaded_bytes = d.get('downloaded_bytes', 0)
            video_item.filesize = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
            video_item.speed = d.get('_speed_str', '')
            video_item.eta = d.get('_eta_str', '')
            
            if video_item.filesize > 0:
                video_item.progress = (video_item.downloaded_bytes / video_item.filesize) * 100
            
            # Update GUI
            self.root.after(0, lambda: self.update_video_display(video_item))
            
        elif d['status'] == 'finished':
            video_item.status = "completed"
            video_item.progress = 100
            video_item.output_filename = d.get('filename', '')
            self.root.after(0, lambda: self.update_video_display(video_item))
    
    def update_video_display(self, video_item):
        """Update the treeview display for a video"""
        values = (
            video_item.title,
            video_item.duration,
            f"{video_item.progress:.1f}%",
            video_item.speed,
            video_item.eta,
            video_item.status,
            "Pause" if video_item.status == "downloading" else "Resume"
        )
        self.videos_tree.item(video_item.id, values=values)
    
    def on_video_double_click(self, event):
        """Handle double-click on video row"""
        item = self.videos_tree.identify_row(event.y)
        if item:
            video = next((v for v in self.videos if v.id == item), None)
            if video:
                if video.status == "downloading":
                    self.pause_video(video)
                elif video.status == "paused":
                    self.resume_video(video)
    
    def pause_video(self, video_item):
        """Pause a specific video download"""
        if video_item.status == "downloading":
            video_item.is_paused = True
            video_item.status = "paused"
            self.update_video_display(video_item)
    
    def resume_video(self, video_item):
        """Resume a paused video download"""
        if video_item.status == "paused":
            video_item.is_paused = False
            video_item.status = "downloading"
            self.update_video_display(video_item)
    
    def pause_all_downloads(self):
        """Pause all active downloads"""
        for video in self.videos:
            if video.status == "downloading":
                self.pause_video(video)
    
    def resume_all_downloads(self):
        """Resume all paused downloads"""
        for video in self.videos:
            if video.status == "paused":
                self.resume_video(video)
    
    def cancel_all_downloads(self):
        """Cancel all downloads"""
        for video in self.videos:
            if video.status in ["downloading", "paused"]:
                video.is_cancelled = True
                video.status = "cancelled"
                self.update_video_display(video)
    
    def log_message(self, message):
        """Add message to status"""
        print(message)  # For debugging
    
    def on_closing(self):
        """Handle window closing"""
        self.cancel_all_downloads()
        self.save_config()
        self.root.destroy()


if __name__ == "__main__":
    YouTubeDownloaderOptimized()
