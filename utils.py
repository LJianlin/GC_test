#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import codecs
import configparser
import argparse


def args_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("conf_path", help="The conf file path", type=str)
    args = parser.parse_args()
    return args


class ParseConf(object):
    def __init__(self, conf_path):
        self.conf_path = conf_path
        self.feed_file = None
        self.result = None
        self.max_depth = 0
        self.crawl_interval = 1  # 抓取间隔. 单位: 秒
        self.crawl_timeout = 2  # 抓取超时. 单位: 秒
        self.thread_count = 1
        self.conf_parse()

    def conf_parse(self):
        conf_parser = configparser.ConfigParser()
        try:
            conf_parser.readfp(codecs.open(self.conf_path, 'r', 'utf-8-sig'))
            self.feed_file = conf_parser.get("spider", "feed_file")
            self.result = conf_parser.get("spider", "result")  # 抓取结果存储文件, 一行一个
            self.max_depth = eval(conf_parser.get("spider", "max_depth"))  # 最大抓取深度(种子为0级)
            self.crawl_interval = eval(conf_parser.get("spider", "crawl_interval"))  # 抓取间隔. 单位: 秒
            self.crawl_timeout = eval(conf_parser.get("spider", "crawl_timeout"))  # 抓取超时. 单位: 秒
            self.thread_count = eval(conf_parser.get("spider", "thread_count") )  # 抓取线程数
        except Exception as e:
            print("Fail to parse conf as Exception: {}".format(e))


class LinkQueue(object):
    def __init__(self):
        # 已访问的url集合
        self.visited_url = []
        # 待访问的url集合
        self.unvisited_url = []

    # 获取访问过的url队列
    def get_visited_url(self):
        return self.visited_url

    # 获取未访问的url队列
    def get_unvisited_url(self):
        return self.unvisited_url

    # 添加到访问过得url队列中
    def add_visited_url(self, url):
        self.visited_url.append(url)

    # 移除访问过得url
    def remove_visited_url(self, url):
        self.visited_url.remove(url)

    # 未访问过得url出队列
    def pop_unvisited_url(self):
        if self.unvisited_url_is_empty():
            return None
        else:
            return self.unvisited_url.pop()

    # 保证每个url只被访问一次
    def add_unvisited_url(self, url):
        if url != "" and url not in self.visited_url and url not in self.unvisited_url:
            self.unvisited_url.insert(0, url)

    # 获得已访问的url数目
    def get_visited_url_count(self):
        return len(self.visited_url)

    # 获得未访问的url数目
    def get_unvisited_url_count(self):
        return len(self.unvisited_url)

    # 判断未访问的url队列是否为空
    def unvisited_url_is_empty(self):
        return len(self.unvisited_url) == 0


