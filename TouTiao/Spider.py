from urllib.parse import urlencode, unquote
import requests
import json
from json.decoder import JSONDecodeError
from bs4 import BeautifulSoup
import re
import pymongo
from Config import *
from hashlib import md5
import os

client = pymongo.MongoClient(MONGO_URL, connect=False)
db = client[MONGO_DB]

def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print('Successfully Saved to Mongo', result)
        return True
    return False

def download_image(url):
    print('Downloading', url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
        return None
    except ConnectionError:
        return None

def save_image(title, content):
    file_path = "{0}/TouTiao/images/{1}".format(os.getcwd(), title)
    folder = os.path.exists(file_path)
    if not folder:
        os.makedirs(file_path)
    file_path = "{0}/{1}.{2}".format(file_path, md5(content).hexdigest(), 'jpg')
    print(file_path)
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)
            f.close()

def get_page_index(offset, keyword):
    data = {
        "aid": 24,
        "app_name": "web_search",
        "offset": offset,
        "format": "json",
        "keyword": keyword,
        "autoload": "true",
        "count": 20,
        "en_qc": 1,
        "cur_tab": 1,
        "from": "search_tab",
        "pd": "synthesis",
        "timestamp": 1561710753640
    }
    params = urlencode(data)
    base = "https://www.toutiao.com/api/search/content/"
    url = base + "?" + params

    headers = {
        "accept": "application/json, text/javascript",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9",
        "content-type": "application/x-www-form-urlencoded",
        "cookie": "tt_webid=6707798690222786051; csrftoken=81e2a3926f6050528c3bb64a27e3efd9; tt_webid=6707798690222786051; WEATHER_CITY=%E5%8C%97%E4%BA%AC; __tasessionId=rhekmo0w71565513934524; s_v_web_id=69956bf7852f67b2053da4b91a45afc2; RT='z=1&dm=toutiao.com&si=z9k1cqk091l&ss=jz6qkqdc&sl=1&tt=0&obo=1'",
        "referer": "https://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36",
        "x-requested-with": "XMLHttpRequest"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            response.encoding = "utf-8"
            return response.text
        return None
    except ConnectionError:
        print("Error occurred")
        return None

def parse_page_index(text):
    try:
        data = json.loads(text)
        if data and 'data' in data.keys():
            for item in data.get('data'):
                article_pattern = re.compile("http://toutiao.com/group/.*", re.S)
                article_url = item.get("article_url")
                if article_url and re.match(article_pattern, article_url):
                    yield item.get('article_url')
    except JSONDecodeError:
        print("JSON Error")

def get_page_detail(url):
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "max-age=0",
        "cookie": "__tasessionId=348iw7mo11561781098529",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        print('Error occurred')
        return None

def parse_page_detail(html, url):
    soup = BeautifulSoup(html, 'lxml')
    title = soup.select('title')[0].get_text()
    images_pattern = re.compile('gallery: JSON.parse\("(.*)"\)', re.S)
    result = re.search(images_pattern, html)
    if result:
        data = json.loads(result.group(1).replace('\\', '').replace("u002F", "/"))
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')
            images = [item.get('url') for item in sub_images]
            for image in images: 
                image = download_image(image)
                save_image(title, image)
            return {
                'title': title,
                'url': url,
                'images': images
            }

def main():
    data = get_page_index(40, "街拍")
    for url in parse_page_index(data):
        html = get_page_detail(url)
        result = parse_page_detail(html, url)
        if result:
            save_to_mongo(result)

if __name__ == "__main__":
    main()