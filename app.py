from flask import Flask, request, jsonify, send_file, Response
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import os
import yt_dlp
from pytubefix import YouTube
app = Flask(__name__)
# Função para buscar o vídeo no YouTube usando cookies
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
            'Cookie': ('VISITOR_PRIVACY_METADATA=CgJCUhIEGgAgJg%3D%3D; __Secure-3PSID=g.a000oAh8TI1n49_Ux3Xu-EC6OlkxjHAXM6x5miSzqwNrlPyElpQL1FzkiQamrdp6Ao-S4wi-jgACgYKAXYSARMSFQHGX2Mi3-ioeMxM6g-eQB45iH09uBoVAUF8yKqEOkk5-7xuugUSgqtZkEQy0076; '
                        'GPS=1; SIDCC=AKEyXzV9rY--p45z6CSNtvGiWYgRv1tmZ0xk5ku9LAwLTk6TIg92JaoPgBTKpof4UyKRI10h; YSC=NKJ1_jqNy2s; '
                        'SID=g.a000oAh8TI1n49_Ux3Xu-EC6OlkxjHAXM6x5miSzqwNrlPyElpQLu-qY3QLRBJ1B02NyeCU05QACgYKAdoSARMSFQHGX2Mi2g4ovCqvp54IpDQMSqD9BRoVAUF8yKpTvReDAG2bpSfUoB3oSW0c0076; '
                        '__Secure-1PSIDTS=sidts-CjEBUFGoh1apV30CyRjKLmKqhixkwGFzC3kI1xjJsPqV06kkxxxuilXeUtnJlWUzZ3_GEAA; '
                        'SAPISID=4CNo5uWwFSZG9b0G/AXzPiQ2L6a2WeVeML; __Secure-1PSIDCC=AKEyXzUympzdridXk38ln7MzIm4DTGYzCRRS3_yY_ZH3yHIZYaI7SbIEzXrE4_5YyinUPpKYnw; SSID=A1_LFRCq0n5oSEBBr; '
                        '__Secure-1PAPISID=4CNo5uWwFSZG9b0G/AXzPiQ2L6a2WeVeML; __Secure-1PSID=g.a000oAh8TI1n49_Ux3Xu-EC6OlkxjHAXM6x5miSzqwNrlPyElpQLF9lbH0035uB1EzYg0VfPHgACgYKAUcSARMSFQHGX2Mi2g4ovCqvp54IpDQMSqD9BRoVAUF8yKp20lbQ6HdFnWbqIeyeKMOe0076; '
                        '__Secure-3PAPISID=4CNo5uWwFSZG9b0G/AXzPiQ2L6a2WeVeML; __Secure-3PSIDCC=AKEyXzUgMP9ByGOSkkpHRFGBaXfHtRTS7_liqfcOXj1pr6ch5kPWlxANCGFhAQ6qc2fLWkK5; '
                        '__Secure-3PSIDTS=sidts-CjEBUFGoh1apV30CyRjKLmKqhixkwGFzC3kI1xjJsPqV06kkxxxuilXeUtnJlWUzZ3_GEAA; '
                        'APISID=DiI70Ovr8Yrz6M30/AxM5EK3i_UXqOsJnU; HSID=A4TGwqBZkE8cI4gFU; '
                        'LOGIN_INFO=AFmmF2swRQIgPGo0mCrlgbAjl1o2BRkL9g19Jzeb_pDpe9qPR7Mx2iUCIQCa8uLKzWF4S0SfQRmEOWSLnvJ2ESqlAMDcJGhAWsYMjw:QUQ3MjNmeVczS1RVb19UQUhxZzBHbnhEWUVyQ204TGVySldjSHdveWJEdmhIeGVUOGdjLW1YSGJqOG5oNDJDOFN1VXBUVEpVQmxmX0FDaUtITjVkMGdEbXVTbDNXX2ZMbGNNb1R6; '
                        'PREF=f6=40000000&tz=America.Fortaleza; VISITOR_INFO1_LIVE=p-s6PkkBDJQ')
        }
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f"ytsearch:{query}", download=True)
        if result:
            video_info = result['entries'][0]
            filename = f"{base_filename}.mp3"
            return filename, video_info['title']
        return None, None

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

@app.route('/play', methods=['GET'])
def play_audio():
    try:
        # Obtém a URL do vídeo
        url = request.args.get("url")
        
        if not url:
            return jsonify({"error": "URL é obrigatória"}), 400
        
        yt = YouTube(url)
        
        # Seleciona apenas o áudio
        stream = yt.streams.filter(only_audio=True).first()
        caminho = stream.download(filename="temp_audio.mp3")  # Baixa temporariamente

        # Reproduz o áudio diretamente como resposta
        def gerar_audio():
            with open(caminho, "rb") as audio:
                data = audio.read(1024)
                while data:
                    yield data
                    data = audio.read(1024)
            os.remove(caminho)  # Remove o arquivo temporário depois de enviar

        return Response(gerar_audio(), mimetype="audio/mpeg")
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/playvideo', methods=['GET'])
def play_video():
    try:
        # Obtém a URL do vídeo
        url = request.args.get("url")
        
        if not url:
            return jsonify({"error": "URL é obrigatória"}), 400
        
        yt = YouTube(url)
        
        # Seleciona o vídeo com a maior resolução
        stream = yt.streams.get_highest_resolution()
        caminho = stream.download(filename="temp_video.mp4")  # Baixa temporariamente

        # Reproduz o vídeo diretamente como resposta
        def gerar_video():
            with open(caminho, "rb") as video:
                data = video.read(1024)
                while data:
                    yield data
                    data = video.read(1024)
            os.remove(caminho)  # Remove o arquivo temporário depois de enviar

        return Response(gerar_video(), mimetype="video/mp4")
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
