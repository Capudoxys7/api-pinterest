from flask import Flask, request, jsonify, redirect, url_for
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import os

app = Flask(__name__)

# Função para baixar arquivos
def download_file(url, filename):
    response = requests.get(url, stream=True)
    file_size = int(response.headers.get('Content-Length', 0))
    progress = tqdm(response.iter_content(1024), f'Downloading {filename}', total=file_size, unit='B', unit_scale=True, unit_divisor=1024)
    
    with open(filename, 'wb') as f:
        for data in progress.iterable:
            f.write(data)
            progress.update(len(data))

# Endpoint para download de vídeo
@app.route('/api/vid', methods=['GET'])
def download_video():
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

# Endpoint para download de imagem
@app.route('/api/img', methods=['GET'])
def download_image():
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

    response = requests.get(img_url, stream=True)
    if response.status_code != 200:
        return jsonify({"error": "Image URL not working"}), 400

    filename = f"{datetime.now().strftime('%d_%m_%H_%M_%S_')}.jpg"
    with open(filename, 'wb') as f:
        f.write(response.content)
    
    return send_file(filename, as_attachment=True)

# Endpoint para obter link de vídeo
@app.route('/api/vid2', methods=['GET'])
def get_video_link():
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

# Endpoint para obter link de imagem
@app.route('/api/img2', methods=['GET'])
def get_image_link():
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

# Endpoint para obter link de vídeo que inicia download automaticamente
@app.route('/api/vid3', methods=['GET'])
def get_video_link_autodownload():
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
    
    return redirect(url_for('download_video_file', video_url=convert_url))

# Endpoint para iniciar download de vídeo
@app.route('/api/download_video_file', methods=['GET'])
def download_video_file():
    video_url = request.args.get('video_url')
    if not video_url:
        return jsonify({"error": "No video URL provided"}), 400
    
    response = requests.get(video_url, stream=True)
    filename = f"{datetime.now().strftime('%d_%m_%H_%M_%S_')}.mp4"
    with open(filename, 'wb') as f:
        f.write(response.content)
    
    return send_file(filename, as_attachment=True)

# Endpoint para obter link de imagem que inicia download automaticamente
@app.route('/api/img3', methods=['GET'])
def get_image_link_autodownload():
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

    return redirect(url_for('download_image_file', img_url=img_url))

# Endpoint para iniciar download de imagem
@app.route('/api/download_image_file', methods=['GET'])
def download_image_file():
    img_url = request.args.get('img_url')
    if not img_url:
        return jsonify({"error": "No image URL provided"}), 400
    
    response = requests.get(img_url, stream=True)
    filename = f"{datetime.now().strftime('%d_%m_%H_%M_%S_')}.jpg"
    with open(filename, 'wb') as f:
        f.write(response.content)
    
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
