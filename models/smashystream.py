from .utils import fetch
from typing import Union
from . import subtitle
import re
import base64
import json
import logging
import asyncio
import threading
import urllib.parse
import requests
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=10)

async def get_imdb_info(imdb: str) -> str:
    api_url = "https://api.themoviedb.org/3/find/" + imdb + "?api_key=0f020a66f3e35379eef31c31363f2176&external_source=imdb_id"
    req = await fetch(api_url, {
        "Host" : "api.themoviedb.org",
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
        "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
    })
    req_data = req.json()
    return req_data

async def handle_server(imdb_id) -> dict:
    # GET SERVER
    req = await fetch("https://embed.smashystream.com/dataaw.php?imdb="+imdb_id, {
        "Referer": "https://player.smashy.stream/",
        "Host" : "embed.smashystream.com",
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
        "Sec-Fetch-Site" : "cross-site"
    })
    req_data = req.json()
    return {
            'data': req_data
        }
async def handle_source(url) -> dict:
    # GET SERVER
    req = await fetch(url, {
        "Referer": "https://player.smashy.stream/",
        "Origin": "https://player.smashy.stream",
        "Host" : "embed.smashystream.com",
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
        "Sec-Fetch-Site" : "cross-site",
        "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
    })
    req_data = req.json()
    return {
            'data': req_data
        }

async def handle_link_in_thread(url: str) -> dict:
    loop = asyncio.get_event_loop()
    # Run handle_link in a separate thread
    return await loop.run_in_executor(executor, handle_link, url)

async def handle_link(url: str) -> dict:
    try:
        logging.debug(f"Fetching URL: {url}")
        req = await fetch(url, {
            "Referer": "https://player.smashy.stream/",
            "Origin": "https://player.smashy.stream",
            "Host": "api.smashystream.top",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
            "Sec-Fetch-Site": "cross-site",
            "Accept": "*/*"
        })
        req_data =  req.json()  # Ensure to await the JSON parsing
        logging.debug(f"Received data: {req_data}")
        return req_data
    except Exception as e:
        logging.error(f"Error fetching URL {url}: {e}")
        return ""
    
    
async def get_server(dbid: str, s: int = None, e: int = None) -> dict:
    try:
       
        movie_info = await get_imdb_info(dbid)
        id = 0
        if movie_info['movie_results'] :
            id = movie_info['movie_results'][0]['id']
        if movie_info['tv_results'] :
            id = movie_info['tv_results'][0]['id']
        links = []
        api_tmdb_links = [
            f"https://api.smashystream.top/api/v1/videovid2t/{id}" + (f"/{s}/{e}" if s and e else ''),
            f"https://api.smashystream.top/api/v1/videoflx/{id}" + (f"/{s}/{e}" if s and e else ''),
            f"https://api.smashystream.top/api/v1/videocat/{id}" + (f"/{s}/{e}" if s and e else ''),
            f"https://api.smashystream.top/api/v1/shortmoviesc/{id}" + (f"/{s}/{e}" if s and e else ''),
            f"https://api.smashystream.top/api/v1/shortvidsr/{id}" + (f"/{s}/{e}" if s and e else ''),
            f"https://api.smashystream.top/api/v1/shortsotv/{id}" + (f"/{s}/{e}" if s and e else ''),
            f"https://api.smashystream.top/api/v1/shortjara/{id}" + (f"/{s}/{e}" if s and e else ''),
            f"https://api.smashystream.top/api/v1/shortfeb/{id}" + (f"/{s}/{e}" if s and e else ''),
            f"https://api.smashystream.top/api/v1/videostc/{id}" + (f"/{s}/{e}" if s and e else ''),
            f"https://api.smashystream.top/api/v1/videoophim/{id}" + (f"/{s}/{e}" if s and e else ''),
            f"https://api.smashystream.top/api/v1/shortrido/{id}" + (f"/{s}/{e}" if s and e else ''),
            f"https://api.smashystream.top/api/v1/videonep/{id}" + (f"/{s}/{e}" if s and e else ''),
            f"https://api.smashystream.top/api/v1/shortfumov/{id}" + (f"/{s}/{e}" if s and e else ''),
            f"https://api.smashystream.top/api/v1/shortkino/{id}" + (f"/{s}/{e}" if s and e else ''),
            f"https://api.smashystream.top/api/v1/videogdp/{id}" + (f"/{s}/{e}" if s and e else '')
        ]
        links.extend(api_tmdb_links)
        api_imdb_links = [
            f"https://api.smashystream.top/api/v1/videomirror/{dbid}" + (f"/{s}/{e}" if s and e else ''),
            f"https://api.smashystream.top/api/v1/videoinsert/{dbid}" + (f"/{s}/{e}" if s and e else ''),
            f"https://api.smashystream.top/api/v1/videoemov/{dbid}" + (f"/{s}/{e}" if s and e else '')
        ]
        links.extend(api_imdb_links)
        sources = []
        stream = []
        
        async def fetch_source(item):
            print("item:", item)
            source_data = await handle_link(item)
            if source_data != "" :
                sources.append(source_data)

        await asyncio.gather(*[fetch_source(item) for item in links])
        for source in sources:
            if source.get('data') and source['data'].get('sources') is not None and len(source['data']['sources']) > 0:
                # Truy cập giá trị của trường 'file'
                file_value = source['data']['sources'][0]['file']
                if file_value.startswith("http"):
                    print("file_value bắt đầu bằng 'http'")
                    stream.append(file_value)
                else:
                    print("hash value:", file_value)
                    result = decrypt(file_value)
                    pattern = r"polished-rain-ab59\.smashystream\.workers\.dev"
                    if re.search(pattern, result):
                        # Tách chuỗi thành các phần tử
                        urls = result.split(',')
                        # Khởi tạo danh sách lưu kết quả
                        parsed_urls = []
                        # Duyệt qua từng phần tử trong danh sách
                        for url in urls:
                            # Tách độ phân giải và URL
                            resolution, link = url.split(']')
                            resolution = resolution.strip('[')  # Loại bỏ dấu '['
                            parsed_urls.append((resolution, link))
                            for resolution, link in parsed_urls:
                                print(f"Resolution: {resolution}, URL: {link}")
                                stream.append(link)
                    else: 
                        if 'https://stream.smashystream.top/proxy/' in result:
                            # Biểu thức chính quy mới
                            pattern = r'http[s]?://[^\s]+\.m3u8'

                            # Tìm tất cả các kết quả khớp
                            matches = re.findall(pattern, result)
                            if matches:
                                for match in matches:
                                    print(f"Link đã trích xuất: {match}")
                                    new_url = match.replace("https://stream.smashystream.top/proxy/", "")
                                    https_links = re.findall(r'https://[^\s"\'<>]+', new_url)
                                    for link in https_links:
                                        stream.append(link)
                                   
                            else:
                                print("Không tìm thấy liên kết phù hợp.")
                        else: 
                            print("result:", result)
                            stream.append(result)
            else:
                print("'data['data']['sources']' is None or empty")
        RESULT = {
            'result': {
                #'data': req_data,
                'sources': stream
            }
        }
        return RESULT
    except Exception as e:
        logging.error(f"Error fetching server data: {e}")
        return {'result': None}
    
async def find_source(location:str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    request = await fetch(location,headers=headers)
    print(request.text)
    data_server = re.findall(r"flex py-2 px-3 rounded-lg w-full -ml-3 hover:bg-opacity-50", request.text)
    return {"data_server":data_server}

async def get_source(url:str):
    RESULT = {}
    RESULT['result'] = await handle_source(url)
    return RESULT

def b1(s):
    return base64.b64encode(urllib.parse.quote(s).encode('utf-8')).decode('utf-8')

def b2(s):
    return urllib.parse.unquote(base64.b64decode(s).decode('utf-8'))

def decrypt(x):
    a = x[2:]
    v = {
        "bk0": "vXch5/GNVBbrXO/Xt", "bk1": "qxO/5lMkx/N5Gjv5J", "bk2": "OVw/M39ryrfCs/yO5", "bk3": "eeAd/OwcV07/Wgo7T", "bk4": "UN/35mMFQjt3/9vst"
    }
    for i in range(4, -1, -1):
        if v[f"bk{i}"] != "":
            a = a.replace("///" + b1(v[f"bk{i}"]), "")

    try:
        data = b2(a)
        v1 = "0"
        v2 = "."
        v3 = "/"
        v4 = "m3u8"
        v5 = "5"
        data = re.sub(r"\{v1\}", v1, data, flags=re.IGNORECASE)
        data = re.sub(r"\{v2\}", v2, data, flags=re.IGNORECASE)
        data = re.sub(r"\{v3\}", v3, data, flags=re.IGNORECASE)
        data = re.sub(r"\{v4\}", v4, data, flags=re.IGNORECASE)
        data = re.sub(r"\{v5\}", v5, data, flags=re.IGNORECASE)
        return data
    except Exception as e:
        print(f"Error: {e}")
        # libs.log({'e': e}, PROVIDER, 'ERROR')
    return ""