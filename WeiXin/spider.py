from urllib.parse import urlencode
import pymongo
import requests
from lxml.etree import XMLSyntaxError
from requests.exceptions import ConnectionError
from pyquery import PyQuery as pq
from config import *
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DB]

base_url = 'https://weixin.sogou.com/weixin?'

headers = {
    'Cookie': 'SUID=BD6B29D24C238B0A5B5AFB930007741B; SUV=00C8177FD2296BAA5B8F6E409DB6F408; IPLOC=CN8100; ABTEST=0|1563191123|v1; weixinIndexVisited=1; sct=6; SNUID=276785B51B1F94F30B6727C81BCC4AC5; JSESSIONID=aaah7zPanJmjW-xTgAoXw; ppinf=5|1565606971|1566816571|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZToxOi58Y3J0OjEwOjE1NjU2MDY5NzF8cmVmbmljazoxOi58dXNlcmlkOjQ0Om85dDJsdU13QUNQWHNLd0w4YXczaUE4Q1dpbm9Ad2VpeGluLnNvaHUuY29tfA; pprdig=IIf8R5ypJjM4cJbyWRgn44vVKJy4_wjiufxtzj37rHQ2RJ26-L91Q-8I6loOzyK8gl55qMWLb2i7Rz6Jot_KZNDWDF3LNzCFD2Hqx5JnyoiWtaDG8h1Oi6e38br9LVNYf0FQSH_R202MmXJkMcottySDMmqKUXP8KHkXS3ynNRg; sgid=11-41943821-AV1RRDv46PrLouacqJJo35g; ppmdig=156560697200000038da85e43df129753dbcfc8afbfc63ef',
    'Host': 'weixin.sogou.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36'
}

proxy = None

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
browser = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(browser, 10)

def get_proxy():
    try:
        response = requests.get(PROXY_POOL_URL)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        return None

def get_html(url, count=1):
    print('Crawling', url)
    print('Trying Count', count)
    global proxy
    if count >= MAX_COUNT:
        print('Tried Too Many Counts')
        return None
    try:
        if proxy:
            proxies = {
                'http': 'http://' + proxy
            }
            response = requests.get(url, allow_redirects=False, headers=headers, proxies=proxies)
        else:
            response = requests.get(url, allow_redirects=False, headers=headers)
        if response.status_code == 200:
            return response.text
        if response.status_code == 302:
            # Need Proxy
            print('302')
            proxy = get_proxy()
            if proxy:
                print('Using Proxy', proxy)
                return get_html(url)
            else:
                print('Get Proxy Failed')
                return None
    except ConnectionError as e:
        print('Error Occurred', e.args)
        proxy = get_proxy()
        count += 1
        return get_html(url, count)

def get_index(keyword, page):
    data = {
        'query': keyword,
        'type': 2,
        'page': page
    }
    queries = urlencode(data)
    url = base_url + queries
    html = get_html(url)
    return html

def parse_index(html):
    doc = pq(html)
    items = doc('.news-box .news-list li .txt-box h3 a').items()
    for item in items:
        yield item.attr('data-share')

def get_detail(url):
    try:
        browser.get(url)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#publish_time')))
        html = browser.page_source
        response = requests.get(url)
        if response.status_code == 200:
            return html
        return None
    except ConnectionError:
        return None

def parse_detail(html):
    try:
        doc = pq(html)
        title = doc('.rich_media_title').text()
        content = doc('.rich_media_content').text()
        date = doc('#publish_time').text()
        nickname = doc('#js_profile_qrcode > div > strong').text()
        wechat = doc('#js_profile_qrcode > div > p:nth-child(3) > span').text()
        return {
            'title': title,
            'content': content,
            'date': date,
            'nickname': nickname,
            'wechat': wechat
        }
    except XMLSyntaxError:
        return None

def save_to_mongo(data):
    if db['articles'].update({'title': data['title']}, {'$set': data}, True):
        print('Saved to Mongo', data['title'])
    else:
        print('Saved to Mongo Failed', data['title'])


def main():
    for page in range(1, 21):
        html = get_index(KEYWORD, page)
        if html:
            article_urls = parse_index(html)
            for article_url in article_urls:
                article_html = get_detail(article_url)
                if article_html:
                    article_data = parse_detail(article_html)
                    print("\n")
                    save_to_mongo(article_data)

if __name__ == "__main__":
    main()