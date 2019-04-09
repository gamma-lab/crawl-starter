# -*- coding: utf-8 -*-

# Scrapy settings for seeking alpha project

import os

BOT_NAME = 'seekingalpha_crawler'

LOG_LEVEL = 'INFO'

CRAWLERA_ENABLED = True if os.getenv('CRAWLERA_ENABLED') is '1' else False
CRAWLERA_APIKEY = os.getenv('CRAWLERA_APIKEY')

SPIDER_MODULES = ['seekingalpha_crawler.spiders']
NEWSPIDER_MODULE = 'seekingalpha_crawler.spiders'

# USER_AGENT = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML,\
#               like Gecko) Chrome/51.0.2704.103 Safari/537.36')

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

SCHEDULER_MEMORY_QUEUE = 'scrapy.squeues.FifoMemoryQueue'
SCHEDULER_DISK_QUEUE = 'scrapy.squeues.PickleFifoDiskQueue'

# sqlite
SQLITE_CONNECTION_STRING = 'sqlite:///earningcall_transcripts.db'

RETRY_HTTP_CODES = [502, 503, 504, 400, 408]


DOWNLOAD_DELAY = 0.5

DOWNLOADER_MIDDLEWARES = {
    'scrapy_crawlera.CrawleraMiddleware': 300,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
}


ITEM_PIPELINES = {
    'seekingalpha_crawler.pipelines.persistDatabase.saveToSqlite': 300,
    'scrapy.pipelines.images.ImagesPipeline': 1
}
