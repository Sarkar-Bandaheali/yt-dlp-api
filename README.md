# YouTube Downloader API

This is a Flask-based API that allows users to download YouTube videos in MP3 or MP4 format. The API uses `yt-dlp` to handle the searchibg, detailing,  downloading and extraction of video/audio content. It also provides a thumbnail URL for the video and a direct download link for the downloaded file.

---

## Features

- **Download YouTube videos as MP3**: Convert and download YouTube videos as MP3 audio files with customizable audio qualities (128kbps, 320kbps, 86kbps, 196kbps, or best available).
- **Download YouTube videos as MP4**: Download YouTube videos in various resolutions (360p, 480p, 720p, 1080p, or best available).
- **Thumbnail Extraction**: Retrieve the thumbnail URL of the YouTube video.
- **Direct Download Link**: Get a direct download link for the downloaded file.

---

## Requirements

- Python 3.7+
- Flask
- yt-dlp
- requests

---

## Installation
- You can run it locally on PC or via termux apk

1. **Clone the repository**:
   ```bash
   git clone https://github.com/mauricegift/yt-dlp.git
   cd yt-dlp
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install `yt-dlp`**:
   ```bash
   pip install yt-dlp
   ```

4. **Create the download directory**:
   Ensure the `download` directory exists in the project root. The API will automatically create it if it doesn't exist.

5. **Run the API**:
   ```bash
   python main.py
   ```

   The API will start on `http://127.0.0.1:5000`.

---

## API Endpoints
- `/` Api json Page(System Info)
- `/api/ytsearch.php` YouTube search only....params => query
- `/api/ytmp4.php` YouTube videos only downloader....params => url
- `/api/ytmp4.php` YouTube audios only downloader....params => url
- `/api/download.php` All platforms media downloader(audio/video)....params => url,type ie &type=mp3 / &type=mp4
- `/api/details.php` Details and available formats of media....params => url

### 1. Download YouTube Video as MP3
- **Endpoint**: `/api/ytmp3.php`
- **Method**: `GET`
- **Parameters**:
  - `url` (required): The YouTube video URL.
  - `quality` (optional): Audio quality. Options: `128k`, `192k`, `256k`, `320k`. Default: `128k`.
- **Example Request**:
  ```
  GET /api/ytmp3.php?url=https://www.youtube.com/watch?v=example&quality=192k
  ```
- **Response**:
  ```json
  {
    "status": 200,
    "success": true,
    "creator": "GiftedTech",
    "thumbnail": "https://example.com/thumbnail.jpg",
    "download_url": "http://127.0.0.1:5000/download/filename.mp3"
  }
  ```

### 2. Download YouTube Video as MP4
- **Endpoint**: `/api/ytmp4.php`
- **Method**: `GET`
- **Parameters**:
  - `url` (required): The YouTube video URL.
  - `format` (optional): Video resolution. Options: `360p`, `480p`, `720p`, `1080p`, `best`. Default: `720p`.
- **Example Request**:
  ```
  GET /api/ytmp4.php?url=https://www.youtube.com/watch?v=example&format=1080p
  ```
- **Response**:
  ```json
  {
    "status": 200,
    "success": true,
    "creator": "GiftedTech",
    "thumbnail": "https://example.com/thumbnail.jpg",
    "download_url": "http://127.0.0.1:5000/download/filename.mp4"
  }
  ```

### 3. Download File
- **Endpoint**: `/download/<filename>`
- **Method**: `GET`
- **Description**: Directly download the file using the filename returned in the MP3/MP4 download response.
- **Example Request**:
  ```
  GET /download/filename.mp4
  ```

---

## Error Responses

- **400 Bad Request**: Missing or invalid parameters.
  ```json
  {
    "status": 400,
    "success": false,
    "creator": "GiftedTech",
    "error": "Youtube URL(Link) is Required"
  }
  ```

- **404 Not Found**: File not found or download failed.
  ```json
  {
    "status": 404,
    "success": false,
    "creator": "GiftedTech",
    "error": "Download Failed, File Not Found"
  }
  ```

- **500 Internal Server Error**: Server-side error during download.
  ```json
  {
    "status": 500,
    "success": false,
    "creator": "GiftedTech",
    "error": "Error message"
  }
  ```

---
