
import unittest
from mini_spider import MiniSpider
import spider_utils

logging = spider_utils.get_simple_logger()

utl = "http://www.baidu.com"


class MiniSpiderTest(unittest.TestCase):
    def test_spider(self):
        logging.info('-' * 10 + "START" + '-' * 10)
        spider = MiniSpider(utl, "./spider.conf")
        spider.crawling()


if __name__ == "__main__":
    unittest.main()
