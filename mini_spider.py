#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup
import socket
import urllib.request as request
import re
import requests
import zlib
import codecs
import configparser
import utils


# utls = "http://cup.baidu.com/spider/"
target_utl = "http://www.baidu.com"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64)\
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
}


class MiniSpider(object):
    def __init__(self, seeds):
        # 初始化当前抓取的深度
        self.current_depth = 0
        self.current_url = None
        # 使用种子初始化url队列
        self.LinkQueue = utils.LinkQueue()
        if isinstance(seeds, str):
            self.LinkQueue.add_unvisited_url(seeds)
        if isinstance(seeds, list):
            for i in seeds:
                self.LinkQueue.add_unvisited_url(i)
        print("Add the seeds url \"%s\" to the unvisited url list" % str(self.LinkQueue.unvisited_url))

    # 抓取过程主函数
    def crawling(self, current_depth):
        while self.current_depth <= current_depth:
            # 循环条件：待抓取的链接不空
            while not self.LinkQueue.unvisited_url_is_empty():
                # 队头url出队列
                self.current_url = self.LinkQueue.pop_unvisited_url()
                # print("Pop out one url \"%s\" from unvisited url list" % visitUrl)
                if self.current_url is None or self.current_url == "":
                    continue
                # 获取超链接
                links = self.get_hyper_links(self.current_url)
                # print("Get %d new links" % len(links))
                # 将url放入已访问的url中
                self.LinkQueue.add_visited_url(self.current_url)
                # print("Visited url count: " + str(self.LinkQueue.getVisitedUrlCount()))
                # print("Visited deepth: " + str(self.current_deepth))
                # 未访问的url入列
                for link in links:
                    self.LinkQueue.add_unvisited_url(link)
                # print("%d unvisited links:" % len(self.LinkQueue.getUnvisitedUrl()))
            self.current_depth += 1

    # 获取源码中得超链接
    def get_hyper_links(self, url):
        links = []
        data = self.get_page_source(url)
        if data[0] == 200:
            soup = BeautifulSoup(data[1])
            link_info = soup.find_all("a", {"href": re.compile('^http|^/{1,2}.')})
            for item in link_info:
                href_value = item.get("href")
                if 'http://' in href_value or 'https://' in href_value:
                    links.append(href_value)
                else:
                    if href_value[1] == '/':
                        href_value = "http:" + href_value
                        print(href_value)
                    else:
                        base_url = self.get_base_url(self.current_url)
                        href_value = "http:" + base_url + href_value
                        print(href_value)

        return links

    # 获取网页源码
    def get_page_source(self, url, timeout=100, coding=None):
        try:
            socket.setdefaulttimeout(timeout)
            response = requests.get(url, headers=headers)
            # html_data = response.content
            html_encoding = response.apparent_encoding
            response.encoding = html_encoding
            # print(html_encoding)
            # print(response.status_code, type(response.status_code))
            # html = unicode(html, "gb2312").encode("utf8")
            # req = request.Request(url)
            # req.add_header('User-agent', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')
            # response = request.urlopen(req)
            # html_data = response.read()  # .decode('utf-8')
            # bs = BeautifulSoup(html_data, "html.parser")
            # img_info = bs.find_all("img")
            # for i in img_info:
            #     print(i.get('src'))


            # page = ''
            # if response.headers.get('Content-Encoding') == 'gzip':
            #     page = zlib.decompress(page, 16 + zlib.MAX_WBITS)
            #
            # if coding is None:
            #     coding = response.headers.getparam("charset")
            # 如果获取的网站编码为None
            # if html_encoding == 'utf-8':
            #     # page = response.read()
            # # 获取网站编码并转化为utf-8
            # else:
            #     # page = response.read()
            #     html_data = html_data.decode(coding).encode('utf-8')
            return [response.status_code, response.text]
        except Exception as e:
            print(str(e))
            return [str(e), None]

    def get_img_links(self, url, timeout=100, coding=None):
        pass

    def get_base_url(self, url):
        data = self.get_page_source(url)
        base_url = data[1]
        return base_url


if __name__ == "__main__":
    spider = MiniSpider(target_utl)
    # spider.crawling(0)
    links = spider.get_hyper_links(target_utl)
#############################################

    # response = requests.get(seeds, headers=headers)
    # html_data = response.text
    # html_encoding = response.apparent_encoding
    # print(html_encoding)
    # # req = request.Request(seeds)
    # # req.add_header('User-agent', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')
    # # response = request.urlopen(req)
    # # html_data = response.read()#.decode('utf-8')
    # print(html_data)
    # # print(response.headers.getparam("charset"))
    # #
    # bs = BeautifulSoup(html_data, "html.parser")
    # # # print(bs.prettify())  # 格式化html结构
    # # # print(bs.title)  # 获取title标签的名称
    # # # print(111111111111111111111111111111111)
    # # # print(bs.title.name)  # 获取title的name
    # # # print(bs.title.string)  # 获取head标签的所有内容
    # # # print(bs.head)
    # # # print(bs.div)  # 获取第一个div标签中的所有内容
    # # # print(bs.div["id"])  # 获取第一个div标签的id的值
    # # # print(bs.a)
    # img_info = bs.find_all("img")
    # print(len(img_info), img_info)
    # for i in img_info:
    #     print(i)
    #     print(i.get('src'))
    # print(111111111111111111111111111111111)
    # link_list = []
    # link_info = bs.find_all("a", {"href": re.compile('//')})
    # print(link_info)
    # for item in link_info:
    #     print(item.get("href"))
    #     # link_list.append(item.get("href"))
    #     # if item["href"].find("http://") != -1:
    #     link_list.append(item.get("href"))
    # # print(link_list)
    # # for i in link_list:
    # #     regex = re.compile('^http|^/')
    # #     x = regex.findall(i)
    # #     print(x)
    # # print(bs.find(id="u1"))  # 获取id="u1"
    # # texts = soup.find_all('div', class_='showtxt')
    # # print(texts)
    # # print(texts[0].text.replace('\xa0' * 8, '\n\n'))
    # #
    # # links = []
    # # data = self.getPageSource(url)
    # # if data[0] == "200":
    # #     soup = BeautifulSoup(data[1])
    # #     a = soup.findAll("a", {"href": re.compile('^http|^/')})
    # #     for i in a:
    # #         if i["href"].find("http://") != -1:
    # #             links.append(i["href"])
    #