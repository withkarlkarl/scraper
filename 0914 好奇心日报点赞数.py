# -*- coding: utf-8 -*-
from selenium import webdriver
from bs4 import BeautifulSoup
from bson.son import SON
from collections import OrderedDict
import time, pymongo

# 连接数据库
client = pymongo.MongoClient('localhost', 27017)
walden = client['qdaily']
article_0914 = walden['article_0914']

# phantomJS加载网页
def main():
    driver = webdriver.PhantomJS(
        executable_path=r'C:\Users\Administrator\Desktop\phantomjs-2.1.1-windows\bin\phantomjs.exe')  # 浏览器的地址
    driver.get("http://www.qdaily.com/")  # 目标网页地址
    # print('##查看：\n', driver.page_source)
    for i in range(7):# 向下拖动 7 次
        try:# 有时会出现“加载更多”的按钮，光拖动没用，需要点击
            driver.find_element_by_link_text("加载更多").click()
            time.sleep(3)
            # print('##查看：\n', driver.page_source)
        except Exception:# 有时不出现按钮，只有拖动才会加载
            driver.execute_script("window.scrollTo(0, 10000)")
            time.sleep(3)
            # print('##查看：\n', driver.page_source)

    # 保存下来
    now_date = time.strftime("%Y_%m_%d", time.localtime())
    with open(now_date + '_Qdaily.html', 'w+') as file:
        file.write(driver.page_source)

    # 传入解析
    soup_parse(driver.page_source)
    driver.close()


# 解析数据，存入数据库
def soup_parse(text):
    print('解析开始……')
    soup = BeautifulSoup(text, 'lxml')
    # 找到文章的div
    article_items = soup.find_all('div', class_="packery-item article animated fadeIn")
    # print(article_items)
    # 每个item是一篇文章
    for item in article_items:
        # 文章分类
        item_tag = item.find('p', class_="category").get_text().strip()
        # 文章标题
        item_title = item.find("h3").get_text().strip()
        # 评论数（有的文章没有评论）
        if item.find('span', class_="iconfont icon-message"):
            item_comments = item.find('span', class_="iconfont icon-message").get_text().strip()
        else:
            item_comments = 0
        # 点赞数（有的文章没有评论点赞）
        if item.find('span', class_="iconfont icon-heart"):
            item_heart = item.find('span', class_="iconfont icon-heart").get_text().strip()
        else:
            item_heart = 0
        # 发布时间
        item_date = item.find('span', class_="smart-date").get_text()
        # 文章地址
        item_url = 'http://www.qdaily.com/' + item.find('a', href=True).get('href')
        print(item_tag)
        print(item_title)
        print(item_comments)
        print(item_heart)
        print(item_date)
        print(item_url)
        # 把数据写入MongoDB
        article_0914.insert_one({
            'tag': item_tag,
            'title': item_title,
            'heart': int(item_heart),
            'date': item_date,
            'url': item_url,
            'comments': int(item_comments)
        })
    # 传入数据分析方法
    mongo_pipe(article_0914)

#
def mongo_pipe(collection):
    # 点赞数最高的10篇文章
    pipeline1 = [
        {"$sort": SON([("heart", -1), ("comments", -1)])},
        # {"$sort": {"heart":1}},
        {"$limit": 10}
    ]
    # 获取日期
    now_date = time.strftime("%Y_%m_%d", time.localtime())

    for i in collection.aggregate(pipeline1):
        i.pop("_id")
        # 按顺序显示，t[0]是key
        l = sorted(i.items(), key=lambda t: (t[0] == 'heart', t[0] == 'comments',
                                               t[0] == 'title', t[0] == 'tag',
                                               t[0] == 'date', t[0] == 'url',), reverse=True)
        print(l)
        with open(now_date + '_top_10_Qdaily.txt', 'a+') as file:
            file.write(str(l)+'\n')

    # 文章种类分布
    pipeline2 = [
        {"$sort": SON([("heart", -1), ("comments", -1)])},
        {"$limit": 10},
        {"$group": {"_id": "$tag", "count": {"$sum": 1}}},
        {"$sort": {"count": 1}}
    ]
    for j in collection.aggregate(pipeline2):
        print(j)
        with open(now_date + '_top_10_Qdaily.txt', 'a+') as file:
            file.write(str(j)+'\n')


# main()
# hhtml = open('Untitled-1.html', 'r', encoding='utf-8').read()
# soup_parse(hhtml)
mongo_pipe(article_0914)

'''
[('heart', 283), ('comments', 41), ('title', '既没文化也没创意的文创产品，谁要买啊？| 好奇心研究所'), ('tag', '商业'), ('date', '9 月 11 日'), ('url', 'http://www.qdaily.com//articles/31991.html')]
[('heart', 273), ('comments', 16), ('title', '新加坡这座植物园一般的豪宅，想就这样代代相传下去'), ('tag', '设计'), ('date', '9 月 12 日'), ('url', 'http://www.qdaily.com//articles/32101.html')]
[('heart', 196), ('comments', 14), ('title', '无论什么灵感，这本笔记本都能记下来｜这个设计了不起'), ('tag', '设计'), ('date', '9 月 12 日'), ('url', 'http://www.qdaily.com//articles/32077.html')]
[('heart', 165), ('comments', 8), ('title', '纽约曼哈顿可能最具创造力的住宅，将在秋天全面完工'), ('tag', '设计'), ('date', '昨天'), ('url', 'http://www.qdaily.com//articles/32130.html')]
[('heart', 126), ('comments', 85), ('title', '我们对新 iPhone 的热情，已经越来越低了 | 好奇心小数据'), ('tag', '智能'), ('date', '9 月 12 日'), ('url', 'http://www.qdaily.com//articles/32091.html')]
[('heart', 112), ('comments', 45), ('title', '大公司头条：支付宝提现也要收手续费了'), ('tag', '商业'), ('date', '9 月 12 日'), ('url', 'http://www.qdaily.com//articles/32079.html')]
[('heart', 101), ('comments', 9), ('title', '大公司头条：Google 和药厂成立合资公司治疗糖尿病，苹果可能下月发布 Mac 的大更新'), ('tag', '智能'), ('date', '昨天'), ('url', 'http://www.qdaily.com//articles/32138.html')]
[('heart', 100), ('comments', 0), ('title', '为无人车做准备，日本开始做给车看的 3D 地图了'), ('tag', '智能'), ('date', '9 月 12 日'), ('url', 'http://www.qdaily.com//articles/31975.html')]
[('heart', 91), ('comments', 5), ('title', '这个德国摄影师，拍摄了上千座残破却美丽的欧洲废弃建筑'), ('tag', '设计'), ('date', '昨天'), ('url', 'http://www.qdaily.com//articles/32136.html')]
[('heart', 87), ('comments', 17), ('title', '2016 年《大都会》宜居城市评选，第一名又是哥本哈根'), ('tag', '设计'), ('date', '昨天'), ('url', 'http://www.qdaily.com//articles/32159.html')]
{'_id': '城市', 'count': 1}
{'_id': '娱乐', 'count': 1}
{'_id': '智能', 'count': 4}
{'_id': '商业', 'count': 7}
{'_id': '设计', 'count': 7}
'''