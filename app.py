from flask import Flask, request, jsonify, send_file
import yt_dlp
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

app = Flask(__name__)

# Função para buscar o vídeo no YouTube usando cookies
def search_video(query):
    ydl_opts = {
    'quiet': True,
    'format': 'bestaudio/best',
    'noplaylist': True,
    'extract-audio': True,
    'audio-format': 'mp3',
    'cookiefile': 'cookies.txt'  # Arquivo de cookies no formato Netscape
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f"ytsearch:{query}", download=False)
        if result:
            return result['entries'][0]
        return None

# Rota para converter vídeo do YouTube em MP3
@app.route('/api/yt/mp3', methods=['GET'])
def get_mp3():
    query = request.args.get('name')
    if not query:
        return jsonify({'error': 'Query não fornecida'}), 400

    video_info = search_video(query)
    if video_info:
        return jsonify({
            'title': video_info['title'],
            'webpage_url': video_info['webpage_url'],
            'duration': video_info['duration']
        })
    else:
        return jsonify({'error': 'Vídeo não encontrado'}), 404

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
