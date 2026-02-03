# YouTube Downloader

A modern desktop application to download YouTube videos, audios, and thumbnails, developed in Python using the CustomTkinter library.

## Features

- **Video**: High-quality download (1080p, 720p, etc.) in MP4 or MKV formats.
- **Audio**: Audio extraction and conversion to MP3 or WAV.
- **Thumbnail**: Video cover download (Thumbnail) in JPG, PNG, or WEBP.
- **Preview**: Automatically displays the thumbnail when pasting the link for confirmation.
- **Settings**: Automatically saves preferred destination folders for each download type.

## Prerequisites

1. **uv**: Ensure you have uv installed to manage the environment and dependencies.
2. **FFmpeg**: Essential for the program to merge video/audio and perform format conversions.
   - Download FFmpeg.
   - Extract and add the FFmpeg `bin` folder to your Windows Environment Variables (PATH).

## Installation and Execution

1. **Clone the repository:**
   ```bash
   git clone https://github.com/LeoSousa155/youtube-downloadder.git
   cd youtube_downloader
   ```

2. **Sync the environment (installs dependencies):**
   ```bash
   uv sync
   ```

3. **Run the program:**
   ```bash
   uv run main.py
   ```

## How to Compile (Create .exe Executable)

Since `PyInstaller` is already included in the project dependencies, simply run the build command via `uv`.

1. **Generate the executable:**
   Run the following command in the terminal, inside the project folder:
   ```bash
   uv run pyinstaller --noconsole --onefile --name="YouTubeDownloader" --collect-all customtkinter main.py
   ```

2. **Locate the file:**
   The `YouTubeDownloader.exe` file will be created in the `dist` folder.