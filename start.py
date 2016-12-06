# -*- coding: utf-8 -*-
# @Author: tongbo.bao
# @Date:   2016-12-02 17:27:41

import random
import requests
import csv
from bs4 import BeautifulSoup

gdata = {}
gdata["data"] = set([])

def get_content(url , data = None):
    header={
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.235'
    }
    timeout = random.choice(range(80, 180))

    rep = requests.get(url, headers = header, timeout = timeout)
    rep.encoding = 'utf-8'

    return rep.text

def start():
    print(gdata["data"])
    a = []
    i = 1
    while i <= 100:
        page = "http://gz.lianjia.com/chengjiao/pg{0}/".format(str(i))
        i += 1
        r = grab(page)
        a.extend(r)
    print(a)
    write_data(a, 'fang.csv')
    print('已经存放到fang.csv')
        
def grab(url):
    print("try to grab page ", url)
    r = get_content(url)

    soup = BeautifulSoup(r, "lxml")

    tradedHoustList = soup.find("ul", class_="listContent").find_all('li')
    temp = []

    if not tradedHoustList:
        return 

    for item in tradedHoustList:
        # 房屋详情链接，唯一标识符
        houseUrl = item.find('div', class_="title").a["href"] or ''

        if houseUrl in gdata["data"]:
            print(houseUrl, " 已经存在，跳过，开始抓取下一个")
            continue

        print('开始抓取' , houseUrl)

        # 抓取 小区，户型，面积
        title = item.find('div', class_="title").a
        if title:
            xiaoqu, houseType, square = (item.find('div', class_="title").a.string.split(" "))
        else:
            xiaoqu, houseType, square = ('Nav', 'Nav', 'Nav')

        # 成交时间，朝向，楼层
        orientation = item.find('div', class_='houseInfo').get_text()
        floor = item.find('div', class_='positionInfo').get_text()
        dealHouseInfo = item.find('div', class_="dealHouseInfo").find('span', class_='dealHouseTxt')
        if dealHouseInfo is None:
            buildInfo = ''
        else:
            buildInfo = dealHouseInfo.find('span').string

        tradeData = item.find("div", class_='dealDate').string
        unitPrice = item.find("div", class_='unitPrice').find("span", class_='number')
        if unitPrice is None:
            perSquarePrice = ''
        else:
            perSquarePrice = unitPrice.string
        totalPriceDiv = item.find("div", class_='totalPrice').find("span", class_='number')
        if totalPriceDiv is None:
            totalPrice = ''
        else:
            totalPrice = totalPriceDiv.string

        temp.append([
            xiaoqu,
            houseType,
            square,
            houseUrl,
            orientation,
            floor,
            buildInfo,
            tradeData,
            perSquarePrice,
            totalPrice,
        ])

        # 添加到已经抓取的池
        gdata["data"].add(houseUrl)

    return temp

def write_data(data, name):
    file_name = name
    with open(file_name, 'a', errors='ignore', newline='') as f:
        f_csv = csv.writer(f)
        f_csv.writerows(data)

start()
