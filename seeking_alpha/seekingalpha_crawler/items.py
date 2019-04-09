# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field
from scrapy.loader.processors import TakeFirst


class Company(Item):
    report_id = Field(output_processor=TakeFirst())
    company_name = Field(output_processor=TakeFirst())
    stock = Field(output_processor=TakeFirst())
    company_participants = Field(output_processor=TakeFirst())
    external_participants = Field(output_processor=TakeFirst())
    published_quarter = Field(output_processor=TakeFirst())
    article_url = Field(output_processor=TakeFirst())
    date_published = Field(output_processor=TakeFirst())
    earning_call_talk = Field(output_processor=TakeFirst())
    question_answers = Field(output_processor=TakeFirst())
    article_title = Field(output_processor=TakeFirst())
    audio_call_url = Field(output_processor=TakeFirst())