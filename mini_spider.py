#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup
import socket
import re
import requests
import zlib
import codecs
import configparser
import utils
import os
from urllib.parse import urlparse
import time


# utl = "http://cup.baidu.com/spider/"
utl = "http://www.baidu.com"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64)\
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
}


class MiniSpider(utils.ParseConf):
    def __init__(self, target_utl, conf_path):
        super().__init__(conf_path)
        self.target_utl = target_utl
        self.current_depth = 0
        self.current_url = ''
        self.current_name = ''
        self.hyper_links = []
        self.img_links = []
        self.LinkQueue = utils.LinkQueue()
        if isinstance(self.target_utl, str):
            self.LinkQueue.add_unvisited_url(self.target_utl)
        if isinstance(self.target_utl, list):
            for i in self.target_utl:
                self.LinkQueue.add_unvisited_url(i)
        print("Add the seeds url \"%s\" to the unvisited url list"
              % str(self.LinkQueue.unvisited_url))

    # 抓取过程主函数
    def crawling(self):
        while self.current_depth <= self.max_depth:
            # 循环条件：待抓取的链接不空
            while not self.LinkQueue.unvisited_url_is_empty():
                # 队头url出队列
                self.current_url = self.LinkQueue.pop_unvisited_url()
                if self.current_url is None or self.current_url == "":
                    continue

                urlparse_result = urlparse(self.current_url)
                self.current_name = urlparse_result.scheme + '://' + urlparse_result.netloc

                data = self.get_page_source(self.current_url, self.crawl_timeout)
                # 获取超链接
                self.hyper_links = self.get_hyper_links(data)
                # 将url放入已访问的url中
                self.LinkQueue.add_visited_url(self.current_url)
                # 未访问的url入列
                for link in self.hyper_links:
                    self.LinkQueue.add_unvisited_url(link)

                # self.get_img_links(data)
            self.current_depth += 1
        # img_links_set = set(self.img_links)
        # with open("./result.txt", 'w', encoding='utf-8') as f:
        #     for item in img_links_set:
        #         f.write(item)

    def get_hyper_links(self, data):
        hyper_links = []
        if data[0] == 200:
            soup = BeautifulSoup(data[1])
            link_info = soup.find_all("a", {"href": re.compile('^http|^/{1,2}.')})
            for item in link_info:
                href_value = item.get("href")
                if re.match('http://|https://', href_value):
                    hyper_links.append(href_value)
                elif re.match('//', href_value):
                    if 'https://' in self.current_name:
                        href_value = 'https:' + href_value
                    elif 'http://' in self.current_name:
                        href_value = 'http:' + href_value
                    hyper_links.append(href_value)
                    print(href_value)
                elif re.match('/', href_value):
                    href_value = self.current_name + href_value
                    hyper_links.append(href_value)
                    print(href_value)
                elif re.match('.+/', href_value):
                    href_value = self.current_url + href_value[1::]
                    hyper_links.append(href_value)
                    print(href_value)
        return hyper_links

    def get_img_links(self, data):
        if data[0] == 200:
            soup = BeautifulSoup(data[1])
            img_info = soup.find_all("img", {"src": re.compile('\.jpg|\.gif|\.png|\.bmp]')})
            for item in img_info:
                href_value = item.get("src")
                if re.match('http://|https://', href_value):
                    self.img_links.append(href_value)
                    print(href_value)
                elif re.match('//', href_value):
                    if 'https://' in self.current_name:
                        href_value = 'https:' + href_value
                    elif 'http://' in self.current_name:
                        href_value = 'http:' + href_value
                    self.img_links.append(href_value)
                    print(href_value)
                elif re.match('/', href_value):
                    href_value = self.current_name + href_value
                    self.img_links.append(href_value)
                    print(href_value)
                elif re.match('.+/', href_value):
                    href_value = self.current_url + href_value[1::]
                    self.img_links.append(href_value)
                    print(href_value)

    def get_page_source(self, url, timeout=10, coding=None):
        time.sleep(self.crawl_interval)
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
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


if __name__ == "__main__":
    # args = utils.args_parse()
    # print(args.conf_path)
    # spider = MiniSpider(utl, args.conf_path)
    spider = MiniSpider(utl, "./spider.conf")
    spider.crawling()

    # utls = "http://cup.baidu.com/spider/"
    # a = ['/aaa', 'bbb/']
    # current_name = "http://cup.baidu.com"
    # result = urlparse(utls)
    # print(result.scheme + '://' + result.netloc)
    # # print(re.match('.+/{1}', utls).group())
    # for i in a:
    #     print(i)
    #     # if re.match('/', i):
    #     #     href_value = current_name + i
    #     #     print(href_value)
    #     if re.match('.+/', i):
    #         href_value = utls + i
    #         print(href_value)
    # print(re.match('h', utls).group())
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