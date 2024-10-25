import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def testar_conexao():
    url = "http://ena.net.playstation.net/netstart/icst"
    headers = {
        "Host": "ena.net.playstation.net",
        "Accept-Language": "pt-BR,pt;q=0.9",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "SceIcst/1.0 libhttp/10.01 (PlayStation 5)",
        "Connection": "keep-alive"
    }

    try:
        resposta = requests.get(url, headers=headers)
        if resposta.status_code == 200:
            print("Conexão estabelecida com sucesso! (HTTP 200 OK)")
            return True
        else:
            print(f"Falha na conexão. Status: {resposta.status_code}")
            return False
    except requests.RequestException as e:
        print(f"Erro de conexão: {e}")
        return False

def testar_download():
    url = "http://gst.prod.dl.playstation.net/networktest/get_192m?p=3&title=NPXS40087"
    headers = {
        "X-CDN": "Level3",
        "Pragma": "akamai-x-cache-on",
        "Host": "gst.prod.dl.playstation.net",
        "User-Agent": "btest/1.0 libhttp/10.01 (PlayStation 5)",
        "Connection": "close"
    }

    try:
        inicio = time.time()
        resposta = requests.get(url, headers=headers, stream=True)
        if resposta.status_code == 200:
            tamanho_bytes = int(resposta.headers.get('content-length', 0))
            total_baixado = 0
            
            with tqdm(total=tamanho_bytes, unit='B', unit_scale=True, desc="Downloading") as pbar:
                for bloco in resposta.iter_content(1024 * 1024):
                    if bloco:
                        total_baixado += len(bloco)
                        pbar.update(len(bloco))
            
            tempo_total = time.time() - inicio
            velocidade_mbps = (total_baixado / (1024 * 1024)) / tempo_total * 8
            
            print(f"Tempo de download: {tempo_total:.2f} segundos")
            print(f"Velocidade de download: {velocidade_mbps:.2f} Mbps")
        else:
            print(f"Erro ao baixar arquivo. Status: {resposta.status_code}")

    except requests.RequestException as e:
        print(f"Erro ao tentar baixar o arquivo: {e}")

def upload_pacote(session, pacote, url):
    headers = {
        "User-Agent": "PS3Application libhttp/4.9.1-000 (CellOS)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "identity",
        "Content-Length": str(len(pacote))
    }
    try:
        resposta = session.post(url, headers=headers, data=pacote, timeout=15)
        return resposta.status_code, len(pacote)
    except requests.RequestException as e:
        print(f"Erro no upload do pacote: {e}")
        return None, 0

def testar_upload(data, url="http://post.net.playstation.net/networktest/post_128", pacote_tamanho=1600, max_workers=8):
    pacotes = [data[i:i+pacote_tamanho] for i in range(0, len(data), pacote_tamanho)]
    total_bytes_enviados = 0
    total_bytes = len(data)

    try:
        inicio = time.time()
        with requests.Session() as session:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(upload_pacote, session, pacote, url): pacote for pacote in pacotes}
                for future in tqdm(as_completed(futures), total=len(futures), desc="Uploading", unit="packages"):
                    status_code, bytes_enviados = future.result()
                    if status_code == 200:
                        total_bytes_enviados += bytes_enviados
                    else:
                        print(f"Falha no upload do pacote. Status: {status_code}")

        tempo_total = time.time() - inicio
        velocidade_mbps = (total_bytes_enviados / (1024 * 1024)) / tempo_total * 8

        print(f"\nUpload completo: {total_bytes_enviados} bytes enviados em {tempo_total:.2f} segundos")
        print(f"Velocidade de upload total: {velocidade_mbps:.2f} Mbps")

    except requests.RequestException as e:
        print(f"Erro ao tentar fazer upload: {e}")

if testar_conexao():
    testar_download()
    data = 'A' * 131072
    testar_upload(data)
else:
    print("O teste de velocidade não será executado, pois a conectividade falhou.")
