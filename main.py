from flask import Flask, request, jsonify, send_file, url_for
import subprocess
import os
import platform
import glob
import json
import requests  

app = Flask(__name__)

DOWNLOAD_PATH = "download"  # Ensure this folder exists
os.makedirs(DOWNLOAD_PATH, exist_ok=True, mode=0o777)

def get_latest_file(ext):
    """ Get the most recent file with the given extension in the downloads directory """
    files = glob.glob(os.path.join(DOWNLOAD_PATH, f"*.{ext}"))
    return max(files, key=os.path.getctime) if files else None

def get_thumbnail(url):
    """ Extract video thumbnail """
    try:
        command = ["yt-dlp", "--get-thumbnail", url]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()  # Thumbnail URL
    except subprocess.CalledProcessError:
        return None  # No thumbnail found

def download_video(url, format, ext, quality="128k"):
    """ Download video/audio and return actual file path """
    output_template = os.path.join(DOWNLOAD_PATH, "%(title)s.%(ext)s")

    command = ["yt-dlp", "-f", format, "-o", output_template]

    # Force MP4 format
    if ext == "mp4":
        command += ["-S", "ext:mp4:m4a", "--merge-output-format", "mp4"]

    # Add audio quality settings for MP3
    if ext == "mp3":
        command += ["--extract-audio", "--audio-format", "mp3", "--audio-quality", quality]

    command.append(url)

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        downloaded_file = get_latest_file(ext)
        
        if not downloaded_file:
            return {
                "status": 404,
                "success": False,
                "creator": "GiftedTech",
                "message": "Download Failed, File Path Not Found!"
            }

        # Get thumbnail
        thumbnail_url = get_thumbnail(url)

        return {
            "status": 200,
            "success": True,
            "creator": "GiftedTech",
            "thumbnail": thumbnail_url,
            "download_url": url_for('serve_file', filename=os.path.basename(downloaded_file), _external=True)
        }

    except subprocess.CalledProcessError as e:
        return {
            "status": 500,
            "success": False,
            "creator": "GiftedTech",
            "error": str(e)
        }


@app.route('/')
def index():
    try:
        # Get IP information
        ip_info = requests.get('https://ipinfo.io/json').json()
        
        # Get RAM usage using os (cross-platform)
        ram_info = {}
        try:
            system = platform.system().lower()
            
            if system == "linux":
                # Linux memory info
                with open('/proc/meminfo') as f:
                    meminfo = f.read()
                total_kb = int(meminfo.split('MemTotal:')[1].split()[0])
                free_kb = int(meminfo.split('MemFree:')[1].split()[0])
                available_kb = int(meminfo.split('MemAvailable:')[1].split()[0])
                
                total = total_kb / (1024 * 1024)  # Convert KB to GB
                free = free_kb / (1024 * 1024)
                available = available_kb / (1024 * 1024)
                used = total - free
                percent = (used / total) * 100
                
            elif system == "darwin":  # macOS
                # macOS memory info
                total_bytes = int(os.popen('sysctl hw.memsize').read().split()[-1])
                vm_stat = os.popen('vm_stat').read().split()
                free_pages = int(vm_stat[vm_stat.index('free:')+1][:-1])
                page_size = 4096  # bytes
                
                total = total_bytes / (1024 ** 3)  # Convert bytes to GB
                free = (free_pages * page_size) / (1024 ** 3)
                used = total - free
                percent = (used / total) * 100
                available = free
                
            elif system == "windows":
                # Windows memory info
                total_bytes = int(os.popen('wmic memorychip get capacity').read().split()[1])
                free_bytes = int(os.popen('wmic OS get FreePhysicalMemory /Value').read().split('=')[1]) * 1024
                
                total = total_bytes / (1024 ** 3)  # Convert bytes to GB
                free = free_bytes / (1024 ** 3)
                used = total - free
                percent = (used / total) * 100
                available = free
                
            else:
                raise Exception(f"Unsupported OS: {system}")
                
            ram_info = {
                "total": f"{total:.2f}GB",
                "used": f"{used:.2f}GB",
                "free": f"{free:.2f}GB",
                "available": f"{available:.2f}GB",
                "usage_percentage": f"{percent:.1f}%"
            }
            
        except Exception as ram_error:
            ram_info = {
                "error": f"RAM info unavailable: {str(ram_error)}",
                "available": False
            }

        return jsonify({
            "status": 200,
            "success": True,
            "creator": "GiftedTech",
            "message": "Ytdlp Api is Running",
            "ip_info": {
                    "address": ip_info.get('ip'),
                    "country": ip_info.get('country'),
                    "city": ip_info.get('city'),
                    "region": ip_info.get('region'),
                    "coordinates": ip_info.get('loc'),
                    "postal_code": ip_info.get('postal'),
                    "isp": ip_info.get('org'),
                    "timezone": ip_info.get('timezone')
                },
                "memory_info": ram_info,
                "platform_info": {
                    "system": platform.system(),
                    "release": platform.release(),
                    "machine": platform.machine()
                }
            }
        })

    except Exception as e:
        return jsonify({
            "status": 200,
            "success": True,
            "creator": "GiftedTech",
            "message": "Ytdlp Api is Running",
            "warning": "Could not fetch system information",
            "error": str(e)
        })


@app.route('/api/ytsearch.php', methods=['GET'])
def ytsearch():
    query = request.args.get('query')
    if not query:
        return jsonify({
            "status": 400,
            "success": False,
            "creator": "GiftedTech",
            "error": "Search query is required"
        }), 400

    try:
        # Get first 10 results 
        command = [
            "yt-dlp",
            "ytsearch10:" + query,
            "--dump-json",
            "--flat-playlist",
            "--skip-download"
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        videos = []
        for line in result.stdout.splitlines():
            data = json.loads(line)
            videos.append({
                "id": data.get('id'),
                "url": data.get('url'),
                "title": data.get('title'),
                "thumbnail": data.get('thumbnail'),
                "artist": data.get('uploader')
            })

        return jsonify({
            "status": 200,
            "success": True,
            "creator": "GiftedTech",
            "results": videos
        })

    except subprocess.CalledProcessError as e:
        return jsonify({
            "status": 500,
            "success": False,
            "creator": "GiftedTech",
            "error": str(e)
        }), 500

@app.route('/api/details.php', methods=['GET'])
def video_details():
    url = request.args.get('url')
    if not url:
        return jsonify({
            "status": 400,
            "success": False,
            "creator": "GiftedTech",
            "error": "URL is required"
        }), 400

    try:
        # Get video details and available formats
        command = [
            "yt-dlp",
            url,
            "--dump-json",
            "--skip-download",
            "--no-warnings"
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)

        # Extract basic info
        info = {
            "id": data.get('id'),
            "title": data.get('title'),
            "thumbnail": data.get('thumbnail'),
            "uploader": data.get('uploader'),
            "duration": data.get('duration'),
            "formats": []
        }

        # Extract available formats
        for fmt in data.get('formats', []):
            format_info = {
                "format_id": fmt.get('format_id'),
                "ext": fmt.get('ext'),
                "resolution": fmt.get('resolution', 'audio'),
                "filesize": fmt.get('filesize'),
                "vcodec": fmt.get('vcodec', 'none'),
                "acodec": fmt.get('acodec', 'none'),
                "format_note": fmt.get('format_note', '')
            }
            info['formats'].append(format_info)

        return jsonify({
            "status": 200,
            "success": True,
            "creator": "GiftedTech",
            "result": info
        })

    except subprocess.CalledProcessError as e:
        return jsonify({
            "status": 500,
            "success": False,
            "creator": "GiftedTech",
            "error": str(e)
        }), 500

# Route for Downloading from multiple platforms not only youtube
@app.route('/api/download.php', methods=['GET'])
def download_media():
    url = request.args.get('url')
    media_type = request.args.get('type')

    if not url:
        return jsonify({
            "status": 400,
            "success": False,
            "creator": "GiftedTech",
            "error": "URL is required"
        }), 400

    if not media_type:
        return jsonify({
            "status": 400,
            "success": False,
            "creator": "GiftedTech",
            "error": "Type parameter is required (mp3 or mp4)"
        }), 400

    if media_type not in ['mp3', 'mp4']:
        return jsonify({
            "status": 400,
            "success": False,
            "creator": "GiftedTech",
            "error": "Invalid type. Use mp3 or mp4"
        }), 400

    # For MP4, get the best quality - 720p
    if media_type == "mp4":
        format_param = "bestvideo[height<=720]+bestaudio/best[height<=720]"
    else:  # MP3
        format_param = "bestaudio"
        media_type = "mp3"

    result = download_video(url, format_param, media_type)
    return jsonify(result)

# Route for Downloading youtube mp3 only with or without quality parameter
@app.route('/api/ytmp3.php', methods=['GET'])
def ytmp3():
    url = request.args.get('url')
    if not url:
        return jsonify({
            "status": 400,
            "success": False,
            "creator": "GiftedTech",
            "error": "Youtube URL(Link) is Required"
        }), 400

    quality = request.args.get('quality', '128k')  # Default quality to 128kbps
    valid_qualities = ["128k", "192k", "256k", "320k"]
    quality = quality if quality in valid_qualities else "128k"

    result = download_video(url, "bestaudio", "mp3", quality)
    return jsonify(result)

# Route for Downloading youtube mp4 only with or without quality parameter
@app.route('/api/ytmp4.php', methods=['GET'])
def ytmp4():
    url = request.args.get('url')
    if not url:
        return jsonify({
            "status": 400,
            "success": False,
            "creator": "GiftedTech",
            "error": "No URL provided"
        }), 400

    # Get format parameter, default quality to 720p
    format_param = request.args.get('format', '720p')

    # Map user-friendly formats to yt-dlp formats
    format_map = {
        "720p": "bestvideo[height<=720]+bestaudio",
        "1080p": "bestvideo[height<=1080]+bestaudio",
        "480p": "bestvideo[height<=480]+bestaudio",
        "360p": "bestvideo[height<=360]+bestaudio",
        "best": "bestvideo+bestaudio",
    }

    # Use mapped format or fallback to user-provided format
    selected_format = format_map.get(format_param, format_param)

    result = download_video(url, selected_format, "mp4")
    return jsonify(result)

@app.route('/download/<filename>', methods=['GET'])
def serve_file(filename):
    """ Serve the downloaded file for direct download (not streaming) """
    file_path = os.path.join(DOWNLOAD_PATH, filename)

    if not os.path.exists(file_path):
        return jsonify({
            "status": 404,
            "success": False,
            "creator": "GiftedTech",
            "error": "Download Failed, File Not Found"
        }), 404

    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000);
