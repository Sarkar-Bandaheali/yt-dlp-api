from flask import Flask, request, jsonify, send_file, url_for
import subprocess
import os
import glob

app = Flask(__name__)

DOWNLOAD_PATH = "download"  # Ensure this folder exists
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

def get_latest_file(ext):
    """ Get the most recent file with the given extension in the downloads directory """
    files = glob.glob(os.path.join(DOWNLOAD_PATH, f"*.{ext}"))
    return max(files, key=os.path.getctime) if files else None

def get_thumbnail(url):
    """ Extract YouTube video thumbnail """
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

    quality = request.args.get('quality', '128k')  # Default quality
    valid_qualities = ["128k", "192k", "256k", "320k"]
    quality = quality if quality in valid_qualities else "128k"

    result = download_video(url, "bestaudio", "mp3", quality)
    return jsonify(result)  # Ensure proper JSON response format

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

    # Get format parameter, default to 720p
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

@app.route('/downloads/<filename>', methods=['GET'])
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
    app.run(debug=True, port=5000)
