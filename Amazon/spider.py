import re
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
from config import *
from selenium.webdriver.chrome.options import Options
import pymongo

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
browser = webdriver.Chrome(options=chrome_options)
# browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)

def search():
    print('正在搜索')
    try:
        browser.get('https://www.amazon.com/')
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#twotabsearchtextbox'))
        )
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#nav-search > form > div.nav-right > div > input')))
        input.send_keys(KEYWORD)
        submit.click()
        total = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#search > div.sg-row > div.sg-col-20-of-24.sg-col-28-of-32.sg-col-16-of-20.sg-col.s-right-column.sg-col-32-of-36.sg-col-8-of-12.sg-col-12-of-16.sg-col-24-of-28 > div > span:nth-child(9) > div > div > div > ul > li:nth-child(6)')))
        get_products()
        return total.text
    except TimeoutException:
        return search()

def next_page():
    print('正在翻页')
    try:
        submit = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '#search > div.sg-row > div.sg-col-20-of-24.sg-col-28-of-32.sg-col-16-of-20.sg-col.s-right-column.sg-col-32-of-36.sg-col-8-of-12.sg-col-12-of-16.sg-col-24-of-28 > div > span:nth-child(9) > div > div > div > ul > li.a-last > a')))
        submit.click()
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#search > div.sg-row > div.sg-col-20-of-24.sg-col-28-of-32.sg-col-16-of-20.sg-col.s-right-column.sg-col-32-of-36.sg-col-8-of-12.sg-col-12-of-16.sg-col-24-of-28 > div > span:nth-child(9) > div > div > div > ul > li.a-selected'))
        )
        get_products()
    except TimeoutException:
        next_page()

def get_products():
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.a-section.a-spacing-medium')))
    html = browser.page_source
    doc = pq(html)
    items = doc('.s-include-content-margin.s-border-bottom').items()
    
    
    for item in items:
        product = {
            'image': item.find('img').attr('src'),
            'price': item.find('.a-price .a-offscreen').text(),
            'title': item.find('.a-text-normal').text()
        }
        save_to_mongo(product)

def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print('存储到MONGODB成功', result)
    except Exception:
        print('存储到MONGODB失败', result)

def main():
    try:
        total = search()
        total = int(total)
        for i in range(2, total + 1):
            next_page()
    except Exception:
        print('出错啦', Exception)
    finally:
        browser.close()

if __name__ == '__main__':
    main()