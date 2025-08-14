# YouTube Playlist Downloader with GUI

A modern, user-friendly Python GUI application for downloading YouTube playlists with quality selection and format options.

## Features

- **Playlist Support**: Download entire YouTube playlists or single videos
- **Quality Selection**: Choose from multiple video quality options (Best, 1080p, 720p, 480p, 360p, Audio Only)
- **Format Options**: Download in MP4, MKV, WebM, or MP3 formats
- **Progress Tracking**: Real-time download progress with detailed logs
- **Custom Download Path**: Select where to save your downloads
- **Resume Support**: yt-dlp handles interrupted downloads automatically
- **Error Handling**: Comprehensive error handling with user-friendly messages

## Installation

1. **Clone or download this repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the application**:
   ```bash
   python youtube_downloader_fixed.py
   ```

2. **Enter a YouTube playlist URL** in the URL field

3. **Select download path** using the Browse button

4. **Choose quality**:
   - Best Quality: Downloads the highest available quality
   - 1080p/720p/480p/360p: Downloads at or below specified resolution
   - Audio Only: Downloads audio only (useful for music)

5. **Select format**:
   - MP4: Most compatible format
   - MKV: Good for high-quality videos
   - WebM: Open source format
   - MP3: Audio only format

6. **Click "Download Playlist"** to start

## Requirements

- Python 3.6 or higher
- yt-dlp (for YouTube downloads)
- tkinter (usually included with Python)

## Troubleshooting

### Common Issues:

1. **"yt-dlp not found" error**:
   - Run: `pip install yt-dlp`

2. **Permission errors**:
   - Ensure you have write permissions to the download directory

3. **Network issues**:
   - Check your internet connection
   - Some videos may be region-restricted

4. **Large playlists**:
   - Downloads may take time for large playlists
   - Progress is saved automatically

## Technical Details

- **Backend**: Uses yt-dlp for reliable YouTube downloads
- **GUI**: Built with tkinter for cross-platform compatibility
- **Threading**: Downloads run in separate threads to keep UI responsive
- **Configuration**: Settings are saved in `downloader_config.json`

## License

This project is open source and available under the MIT License.
