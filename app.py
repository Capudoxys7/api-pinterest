from flask import Flask, request, jsonify, send_file, Response
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import os
import yt_dlp
from pytubefix import YouTube
app = Flask(__name__)
from datetime import datetime
import yt_dlp

def search_video(query):
    # Gerar um nome base para o arquivo com data e hora
    base_filename = datetime.now().strftime('%Y%m%d_%H%M%S')
    ydl_opts = {
        'quiet': True,
        'format': 'bestaudio/best',
        'noplaylist': True,
        'extract-audio': True,
        'audio-format': 'mp3',
        'outtmpl': f'{base_filename}.%(ext)s',  # Nome do arquivo com data e hora
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'http_headers': {
            'Cookie': (
                'Tx0HzHag7kznH9g%3AQUQ3MjNmendfaFZoSjM0b1NKNXZtUW1sbkRhQTVUajJ6Q2I5RHNIRnRJZzJYSUxoTVdVbS1tVHA3c3JhZHRsMjdiN2dqQldybDMwSmk3clVNVDV1dVNrU1QweGc5NzlqRnB3eG5zZ3RvWmJvOEZaLWJKSUduU0FpRTFTSEk2VHdkeVFkbmFqUVVjNHZIX3F6bXlnYlhYTFZrRG5mbnVVQXBB; '
                '__Secure-1PSID=g.a000pgh8TJ84cLMDzZBqDTalAQ8CAqr554JjJfBm7GCWrk2AihspiC4G-jnKTCXRVLALESOJzgACgYKAdoSARMSFQHGX2MiVaydOyPuv4YOgOdQaUm1GBoVAUF8yKpkrOptS9lgL4dAIwZF4Urv0076; '
                '__Secure-3PSID=g.a000pgh8TJ84cLMDzZBqDTalAQ8CAqr554JjJfBm7GCWrk2AihspiC4G-jnKTCXRVLALESOJzgACgYKAdoSARMSFQHGX2MiVaydOyPuv4YOgOdQaUm1GBoVAUF8yKpkrOptS9lgL4dAIwZF4Urv0076; '
                'HSPORT_SESSIONID=G6gN3sWrKX; '
                'ST-ycseu=; '
                '__Secure-3PSIDTS=sidts-CjEBQT4rXyfDIfRTXfL8o8Yzhh-w_50h3LP_EqN6RmhSKFc_xCg5z_ZSRGbaCYe3AH9YEAA; '
                'G_ENABLED_IDPS=google; '
                'YSC=fzIPzRQQAvs; '
                'hs2_9kk7=; '
                'ST-xuwub9=session_logininfo=AFmmF2swRQIhAOPaSjZd9B1D54ockSjNurILnr_DoWyBAHCsbtTM6sOjAiAuFTLMyER65c3V-nLgE2wGiimBo6yTx0HzHag7kznH9g%3AQUQ3MjNmendfaFZoSjM0b1NKNXZtUW1sbkRhQTVUajJ6Q2I5RHNIRnRJZzJYSUxoTVdVbS1tVHA3c3JhZHRsMjdiN2dqQldybDMwSmk3clVNVDV1dVNrU1QweGc5NzlqRnB3eG5zZ3RvWmJvOEZaLWJKSUduU0FpRTFTSEk2VHdkeVFkbmFqUVVjNHZIX3F6bXlnYlhYTFZrRG5mbnVVQXBB; '
                'ST-g3o9e9=session_logininfo=AFmmF2swRQIhAOPaSjZd9B1D54ockSjNurILnr_DoWyBAHCsbtTM6sOjAiAuFTLMyER65c3V-nLgE2wGiimBo6yTx0HzHag7kznH9g%3AQUQ3MjNmendfaFZoSjM0b1NKNXZtUW1sbkRhQTVUajJ6Q2I5RHNIRnRJZzJYSUxoTVdVbS1tVHA3c3JhZHRsMjdiN2dqQldybDMwSmk3clVNVDV1dVNrU1QweGc5NzlqRnB3eG5zZ3RvWmJvOEZaLWJKSUduU0FpRTFTSEk2VHdkeVFkbmFqUVVjNHZIX3F6bXlnYlhYTFZrRG5mbnVVQXBB'
            )
        },
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Extrai e baixa o áudio
            result = ydl.extract_info(f"ytsearch:{query}", download=True)
            if result and 'entries' in result and len(result['entries']) > 0:
                print(f"Download completo: {base_filename}.mp3")
                return f"{base_filename}.mp3"  # Retorna o nome do arquivo baixado
        except Exception as e:
            print(f"Erro ao baixar áudio: {e}")

    return None

# Rota para baixar o vídeo do YouTube e enviar o arquivo MP3
@app.route('/api/yt/mp3', methods=['GET'])
def get_mp3():
    query = request.args.get('name')
    if not query:
        return jsonify({'error': 'Query não fornecida'}), 400

    # Baixa o vídeo com base na pesquisa
    filename, _ = search_video(query)
    
    if filename and os.path.isfile(filename):
        # Envia o arquivo como resposta
        return send_file(
            filename,
            as_attachment=True,
            download_name=filename,
            mimetype="audio/mpeg"
        )
    else:
        return jsonify({'error': 'Falha ao baixar ou encontrar o vídeo'}), 500

@app.route('/api/yt/play', methods=['GET'])
def get_mp3_info():
    query = request.args.get('name')
    if not query:
        return jsonify({'error': 'Query não fornecida'}), 400

    # Busca o vídeo e obtém as informações
    with yt_dlp.YoutubeDL({'quiet': True, 'format': 'bestaudio/best', 'noplaylist': True}) as ydl:
        result = ydl.extract_info(f"ytsearch:{query}", download=True)
        if result:
            video_info = result['entries'][0]
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
            title = video_info['title']
            upload_date = video_info.get('upload_date', 'N/A')
            views = video_info.get('view_count', 'N/A')
            thumbnail = video_info.get('thumbnail', 'N/A')
            channel = video_info.get('uploader', 'N/A')

            # Cria o link de download acessível externamente
            download_link = request.host_url + 'api/yt/mp3?name=' + query

            # Cria a resposta com as informações do vídeo
            response = {
                'title': title,
                'download_link': download_link,
                'upload_date': upload_date,
                'views': views,
                'thumbnail': thumbnail,
                'channel': channel
            }
            return jsonify(response)
        else:
            return jsonify({'error': 'Falha ao baixar ou encontrar o vídeo'}), 500

# Endpoint para baixar e retornar vídeo diretamente
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

# Endpoint para baixar e retornar imagem diretamente
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

    filename = f"{datetime.now().strftime('%d_%m_%H_%M_%S_')}.jpg"
    download_file(img_url, filename)
    
    return send_file(filename, as_attachment=True)

# Endpoint para obter link direto do vídeo
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

# Endpoint para obter link direto da imagem
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

@app.route('/api/yt/mp3', methods=['GET'])
def download_mp3():
    query = request.args.get('name')
    if not query:
        return jsonify({'error': 'Query não fornecida'}), 400

    # Gerar um nome base para o arquivo com data e hora
    base_filename = datetime.now().strftime('%Y%m%d_%H%M%S')
    ydl_opts = {
        'quiet': True,
        'format': 'bestaudio/best',
        'noplaylist': True,
        'extract-audio': True,
        'audio-format': 'mp3',
        'outtmpl': f'{base_filename}.%(ext)s',  # Nome do arquivo com data e hora
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Extrai e baixa o áudio
            result = ydl.extract_info(f"ytsearch:{query}", download=True)
            if result and 'entries' in result and len(result['entries']) > 0:
                video_info = result['entries'][0]
                filename = f"{base_filename}.mp3"
                return send_file(
                    filename,
                    as_attachment=True,
                    download_name=filename,
                    mimetype="audio/mpeg"
                )
        except Exception as e:
            print(f"Error downloading audio: {e}")
            return jsonify({'error': 'Falha ao baixar o áudio'}), 500

    return jsonify({'error': 'Nenhum resultado encontrado'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
