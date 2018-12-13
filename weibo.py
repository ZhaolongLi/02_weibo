# coding:utf-8

from urllib.parse import urlencode
from pyquery import PyQuery as pq
from pymongo import MongoClient
import requests


base_url = 'https://m.weibo.cn/api/container/getIndex?'
headers = {
    'Host':'m.weibo.cn',
    'Referer':'https://m.weibo.cn/u/2830678474',
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) '
                         'AppleWebKit/535.11 (KHTML, like Gecko) Chrome/' 
                         '17.0.963.56 Safari/535.11',
    'X-Requested-With':'XMLHttpRequest',
}

def get_page(page):
    """
    获取页面内容
    :param page:
    :return:
    """
    params = {
        'type':'uid',
        'value':'2830678474',
        'containerid':'1076032830678474',
        'page':page
    }
    url = base_url + urlencode(params) # 对url进行编码
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return response.json() # 将内容解析为json返回
    except requests.ConnectionError as e:
        print('Error',e.args)

def parse_page(json):
    """
    解析页面内容
    :param json:
    :return:
    """
    if json:
        items = json.get('data').get('cards')
        for item in items:
            item = item.get('mblog')
            if item:
                weibo = {}
                weibo['id'] = item.get('id')
                weibo['text'] = pq(item.get('text')).text() # 将正文中标签去掉
                weibo['attitudes'] = item.get('attitudes_count')
                weibo['comments'] = item.get('comments_count')
                weibo['reposts'] = item.get('reposts_count')
                yield weibo
            else:
                return None

def save_to_mongo(result):
    """
    将爬取的内容写入mongodb数据库
    :param result:
    :return:
    """
    if collection.insert(result):
        print('Saved to Mongo')

if __name__ == '__main__':
    client = MongoClient(host='localhost',port=27017) # 创建mongodb连接
    db = client['weibo']
    collection = db['weibo']
    for page in range(1,11):
        json = get_page(page)
        results = parse_page(json)
        for result in results:
            # print(result)
            save_to_mongo(result)
