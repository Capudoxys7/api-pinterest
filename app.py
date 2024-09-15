from flask import Flask, request, jsonify, send_file
import yt_dlp
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

app = Flask(__name__)

# Função para pesquisar vídeos no YouTube
def search_video(query):
    ydl_opts = {'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            search_result = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
            return search_result['webpage_url']
        except Exception as e:
            print(f"Error searching video: {e}")
            return None

# Função para baixar vídeos do YouTube
def download_video(url, format):
    ydl_opts = {
        'format': 'bestaudio/best' if format == 'mp3' else 'bestvideo+bestaudio',
        'outtmpl': f'%(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }] if format == 'mp3' else []
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            print(f"Downloaded info dict: {info_dict}")
            filename = ydl.prepare_filename(info_dict)
            if format == 'mp3':
                filename = filename.rsplit('.', 1)[0] + '.mp3'
            print(f"Final filename: {filename}")
            return filename
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None

# Função para baixar arquivos
def download_file(url, filename):
    response = requests.get(url, stream=True)
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)

# Endpoint para baixar vídeos do YouTube
@app.route('/api/yt/<format>', methods=['GET'])
def download(format):
    if format not in ['mp3', 'mp4']:
        return jsonify({"error": "Invalid format. Use 'mp3' or 'mp4'."}), 400

    name = request.args.get('name')
    url = request.args.get('url')

    if not name and not url:
        return jsonify({"error": "Missing 'name' or 'url' parameter."}), 400

    if name:
        url = search_video(name)
        if not url:
            return jsonify({"error": "Video not found."}), 404

    filename = download_video(url, format)
    if not filename or not os.path.exists(filename):
        return jsonify({"error": "Failed to download video."}), 500

    try:
        return send_file(filename, as_attachment=True)
    finally:
        if filename and os.path.exists(filename):
            os.remove(filename)

# Endpoint para baixar vídeos diretamente de links do Pinterest
@app.route('/api/vid', methods=['GET'])
def download_pinterest_video():
    url = request.args.get('url')
    if not url or ("pinterest.com/pin/" not in url and "https://pin.it/" not in url):
        return jsonify({"error": "Invalid URL"}), 400
    
    if "https://pin.it/" in url:
        t_body = requests.get(url)
        if t_body.status_code != 200:
            return jsonify({"error": "URL not working"}), 400
        soup = BeautifulSoup(t_body.content, "html.parser")
        href_link = soup.find("link", rel="alternate")['href']
        match = re.search('url=(.*?)&', href_link)
        url = match.group(1)
    
    body = requests.get(url)
    if body.status_code != 200:
        return jsonify({"error": "URL not working"}), 400
    
    soup = BeautifulSoup(body.content, "html.parser")
    extract_url = soup.find("video", class_="hwa kVc MIw L4E")['src']
    convert_url = extract_url.replace("hls", "720p").replace("m3u8", "mp4")

    filename = f"{datetime.now().strftime('%d_%m_%H_%M_%S_')}.mp4"
    download_file(convert_url, filename)
    
    return send_file(filename, as_attachment=True)

# Endpoint para baixar imagens diretamente de links do Pinterest
@app.route('/api/img', methods=['GET'])
def download_pinterest_image():
    url = request.args.get('url')
    if not url or ("pinterest.com/pin/" not in url and "https://pin.it/" not in url):
        return jsonify({"error": "Invalid URL"}), 400

    t_body = requests.get(url)
    if t_body.status_code != 200:
        return jsonify({"error": "URL not working"}), 400
    
    soup = BeautifulSoup(t_body.content, "html.parser")
    img_tag = soup.find("img")
    if img_tag is None:
        return jsonify({"error": "No image found"}), 404
    
    img_url = img_tag['src']
    if not img_url.startswith(('http:', 'https:')):
        img_url = f"https:{img_url}"

    filename = f"{datetime.now().strftime('%d_%m_%H_%M_%S_')}.jpg"
    download_file(img_url, filename)
    
    return send_file(filename, as_attachment=True)

# Endpoint para obter link direto de vídeo do Pinterest
@app.route('/api/vid2', methods=['GET'])
def get_pinterest_video_link():
    url = request.args.get('url')
    if not url or ("pinterest.com/pin/" not in url and "https://pin.it/" not in url):
        return jsonify({"error": "Invalid URL"}), 400
    
    if "https://pin.it/" in url:
        t_body = requests.get(url)
        if t_body.status_code != 200:
            return jsonify({"error": "URL not working"}), 400
        soup = BeautifulSoup(t_body.content, "html.parser")
        href_link = soup.find("link", rel="alternate")['href']
        match = re.search('url=(.*?)&', href_link)
        url = match.group(1)
    
    body = requests.get(url)
    if body.status_code != 200:
        return jsonify({"error": "URL not working"}), 400
    
    soup = BeautifulSoup(body.content, "html.parser")
    extract_url = soup.find("video", class_="hwa kVc MIw L4E")['src']
    convert_url = extract_url.replace("hls", "720p").replace("m3u8", "mp4")
    
    return jsonify({"video_url": convert_url})

# Endpoint para obter link direto de imagem do Pinterest
@app.route('/api/img2', methods=['GET'])
def get_pinterest_image_link():
    url = request.args.get('url')
    if not url or ("pinterest.com/pin/" not in url and "https://pin.it/" not in url):
        return jsonify({"error": "Invalid URL"}), 400

    t_body = requests.get(url)
    if t_body.status_code != 200:
        return jsonify({"error": "URL not working"}), 400
    
    soup = BeautifulSoup(t_body.content, "html.parser")
    img_tag = soup.find("img")
    if img_tag is None:
        return jsonify({"error": "No image found"}), 404
    
    img_url = img_tag['src']
    if not img_url.startswith(('http:', 'https:')):
        img_url = f"https:{img_url}"

    return jsonify({"image_url": img_url})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
