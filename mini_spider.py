#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup
import socket
import re
import requests
import zlib
import codecs
import configparser
import spider_utils
import os
import urllib.request
from urllib.parse import urlparse
import time
from queue import Queue
import traceback
import threading
import sys


logging = spider_utils.get_simple_logger()

# utl = "http://cup.baidu.com/spider/"
utl = "http://www.baidu.com"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64)\
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
}


class MiniSpider(spider_utils.ParseConf):
    def __init__(self, target_utl, conf_path):
        super().__init__(conf_path)
        self.target_utl = target_utl
        self.current_depth = 0
        self.current_url = ''
        self.current_name = ''
        self.hyper_links = spider_utils.MultipleLinkQueue(100000)
        self.LinkQueue = spider_utils.MultipleLinkQueue(100000)
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
            print("current_depth : {}".format(self.current_depth))
            while not self.LinkQueue.unvisited_url_is_empty():
                for index in range(self.thread_count):
                    consumer_thread = threading.Thread(target=self.consumer, args=(self.LinkQueue, self.hyper_links,))
                    consumer_thread.daemon = True
                    consumer_thread.start()
            self.LinkQueue.join()
            print("===============================")
            print("Get hyper_links num :", self.hyper_links.qsize())
            print("===============================")
            while self.hyper_links.qsize() > 0:
                link = self.hyper_links.get()
                self.LinkQueue.add_unvisited_url(link)
            self.current_depth += 1
        print(self.LinkQueue.img_links)
        # img_links_set = set(self.img_links)
        # with open("./result.txt", 'w', encoding='utf-8') as f:
        #     for item in img_links_set:
        #         f.write(item + '\n')

    def get_hyper_links(self, data):
        if data[0] == 200:
            try:
                hyper_links = []
                soup = BeautifulSoup(data[1], from_encoding="iso-8859-1")
                # from_encoding="iso-8859-1"
                # 解决WARNING:Some characters could not be decoded, and were replaced with REPLACEMENT CHARACTER.
                link_info = soup.find_all("a", {"href": re.compile('^http|^/{1,2}.')})  # 网址筛选
                for item in link_info:
                    href_value = item.get("href")
                    # 正则补全网址
                    if re.match('http://|https://', href_value):
                        hyper_links.append(href_value)
                    elif re.match('//', href_value):
                        if 'https://' in self.current_name:
                            href_value = 'https:' + href_value
                        elif 'http://' in self.current_name:
                            href_value = 'http:' + href_value
                        hyper_links.append(href_value)
                        # print(href_value)
                    elif re.match('/', href_value):
                        href_value = self.current_name + href_value
                        hyper_links.append(href_value)
                        # print(href_value)
                    elif re.match('.+/', href_value):
                        href_value = self.current_url + href_value[1::]
                        hyper_links.append(href_value)
                        # print(href_value)
                return hyper_links
            except Exception as e:
                logging.error(e)
                logging.debug(traceback.format_exc())
                return []
        else:
            return []

    def get_img_links(self, soup):
        img_info = soup.find_all("img", {"src": re.compile('\.jpg|\.gif|\.png|\.bmp')})  # 图片网址筛选
        for item in img_info:
            href_value = item.get("src")
            # 正则补全网址
            if re.match('http://|https://', href_value):
                self.LinkQueue.img_links.add(href_value)
            elif re.match('//', href_value):
                if 'https://' in self.current_name:
                    href_value = 'https:' + href_value
                elif 'http://' in self.current_name:
                    href_value = 'http:' + href_value
                self.LinkQueue.img_links.add(href_value)
            elif re.match('/', href_value):
                href_value = self.current_name + href_value
                self.LinkQueue.img_links.add(href_value)
            elif re.match('.+/', href_value):
                href_value = self.current_url + href_value[1::]
                self.LinkQueue.img_links.add(href_value)

    def get_page_source(self, url, timeout=10):
        time.sleep(self.crawl_interval)
        try:
            req = urllib.request.Request(url, headers=headers)
            response = urllib.request.urlopen(req, timeout=timeout)
            content_type = response.info().get("Content-Type")
            coding = []
            if re.match('text/html', content_type):  # 判断是否是下载链接
                # 编码转换
                request_get = requests.get(url, headers=headers, timeout=timeout)
                coding.append(request_get.apparent_encoding)
                coding.append(request_get.encoding)
                if 'charset=' in content_type:
                    coding = []
                    coding.append(content_type.split('=')[1])
                print(coding)
                if 'utf-8' in coding or 'UTF-8' in coding:
                    html_data = response.read()
                elif 'gzip' in coding:
                    html_data = response.read()
                    html_data = zlib.decompress(html_data, 16 + zlib.MAX_WBITS).decode("utf-8")
                elif 'GB2312' in coding or 'gb18030' in coding or 'gb2312' in coding or 'GB18030' in coding:
                    html_data = response.read().decode("gb18030").encode("utf-8")
                else:
                    html_data = response.read().decode(coding[-1]).encode("utf-8")

                hyper_links = []
                if response.getcode() == 200:
                    soup = BeautifulSoup(html_data, from_encoding="iso-8859-1")
                    # from_encoding="iso-8859-1"
                    # 解决WARNING:Some characters could not be decoded, and were replaced with REPLACEMENT CHARACTER.
                    link_info = soup.find_all("a", {"href": re.compile('^http|^/{1,2}.')})  # 网址筛选
                    for item in link_info:
                        href_value = item.get("href")
                        # 正则补全网址
                        if re.match('http://|https://', href_value):
                            hyper_links.append(href_value)
                        elif re.match('//', href_value):
                            if 'https://' in self.current_name:
                                href_value = 'https:' + href_value
                            elif 'http://' in self.current_name:
                                href_value = 'http:' + href_value
                            hyper_links.append(href_value)
                        elif re.match('/', href_value):
                            href_value = self.current_name + href_value
                            hyper_links.append(href_value)
                        elif re.match('.+/', href_value):
                            href_value = self.current_url + href_value[1::]
                            hyper_links.append(href_value)
                    self.get_img_links(soup)
                else:
                    logging.error("response.getcode() != 200")
                    logging.error("The error URL: {}".format(url))
                return hyper_links
            else:
                return []
        except Exception as e:
            logging.error(e)
            logging.error("The error URL: {}".format(url))
            # logging.debug(traceback.format_exc())
            return []

    def consumer(self, in_q, out_q):  # 消费者
        # 从inq里放入取出访问的url，得到所需数据。
        if not in_q.unvisited_url_is_empty():
            # 队头url出队列
            self.current_url = in_q.pop_unvisited_url()
            print("current_depth : {}, current_url : {}".format(self.current_depth, self.current_url))
            if self.current_url is None or self.current_url == "":
                pass
            # 获取链接域名，用于补全相对路径网址
            urlparse_result = urlparse(self.current_url)
            self.current_name = urlparse_result.scheme + '://' + urlparse_result.netloc

            # 获取超链接
            hyper_links_get = self.get_page_source(self.current_url, self.crawl_timeout)
            # 将url放入已访问的url中
            self.LinkQueue.add_visited_url(self.current_url)

            if len(hyper_links_get) > 0:
                for link in hyper_links_get:
                    out_q.put(link)
            time.sleep(1)
            in_q.task_done()

    # def producer(self, in_q, out_q):  # 生产者
    #     while True:
    #         print("self.current_depth ", self.current_depth)
    #         print("self.max_depth ", self.max_depth)
    #         if self.LinkQueue.unvisited_url_is_empty():
    #             self.LinkQueue.join()
    #             if self.hyper_links.qsize() > 0:
    #                 self.current_depth += 1
    #         if self.current_depth <= self.max_depth:
    #             for i in range(self.hyper_links.qsize()):
    #                 link = self.hyper_links.get()
    #                 self.LinkQueue.add_unvisited_url(link)


# if __name__ == "__main__":
#     logging.info('-'*10 + "START" + '-'*10)
#     spider = MiniSpider(utl, "./spider.conf")
#     spider.crawling()
    # print(spider.LinkQueue.qsize())
    # in_q = Queue()
    # in_q.put(utl)
    # producer_thread = threading.Thread(target=producer, args=(in_q,))
    # # producer_thread.daemon = True
    # producer_thread.start()

    # for index in range(10):
    #     consumer_thread = threading.Thread(target=spider.consumer, args=(queue, result_queue,))
    #     consumer_thread.daemon = True
    #     consumer_thread.start()
    # #
    # queue.join()
    # end = time.time()
    # print('总耗时：%s' % (end - start))
    # print('queue 结束大小 %d' % queue.qsize())
    # print('result_queue 结束大小 %d' % result_queue.qsize())


    # url = 'http://news.baidu.com/guoji'
    # print(type(url))
    # coding = requests.get(url, headers=headers, timeout=10).apparent_encoding
    # print(coding)
    # req = urllib.request.Request(url, headers=headers)
    # response = urllib.request.urlopen(req, timeout=10)
    # content_type = response.info().get("Content-Type")
    # print(content_type)
    # if 'charset=' in content_type:
    #     print(content_type.split('=')[1])
    # print(dir(requests.get(url, headers=headers, timeout=10)))
    # print(requests.get(url, headers=headers, timeout=10).encoding)
    # resp = urllib.request.urlopen(utl)
    #
    # HttpMessage = resp.info()
    # ContentType = HttpMessage.get("Content-Type")
    # print(type(ContentType))
    # print(HttpMessage.get("Content-Type"))
    # if re.match('text/html', ContentType):
    #     print(1)
    # if 'charset=' in ContentType:
    #     print(ContentType.split('=')[1])
    #     print()
    # x = re.compile('charset=.*').findall(ContentType)
    # print(str(x).split('=')[1])
    # response = requests.get(url, headers=headers)
    # print(response.text)
    # start = time.time()
    # queue = spider_utils.MultipleLinkQueue(100)
    # # print(dir(queue))
    # result_queue = Queue()
    # # print('queue 开始大小 %d' % queue.qsize())
    # for i in range(100):
    #     queue.add_unvisited_url(i)

    # producer_thread = threading.Thread(target=spider.producer, args=(spider.LinkQueue,))
    # producer_thread.daemon = True
    # producer_thread.start()
    # # print(queue.qsize())
    # # for i in range(10):
    # #     print(queue.get())
    # # print(queue.qsize())
    # # queue.put('a')
    # # print(queue.qsize())
    # # print(queue.get())
    # for index in range(10):
    #     consumer_thread = threading.Thread(target=spider.consumer, args=(queue, result_queue,))
    #     consumer_thread.daemon = True
    #     consumer_thread.start()
    # #
    # queue.join()
    # end = time.time()
    # print('总耗时：%s' % (end - start))
    # print('queue 结束大小 %d' % queue.qsize())
    # print('result_queue 结束大小 %d' % result_queue.qsize())

