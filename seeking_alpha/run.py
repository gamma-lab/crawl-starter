# -*- coding: utf-8 -*-
import warnings
warnings.filterwarnings("ignore")

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from seekingalpha_crawler.spiders.seekingalpha \
    import SeekingAlphaSpider

if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl(SeekingAlphaSpider)
    process.start()
