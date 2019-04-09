# -*- coding: utf-8 -*-
import scrapy
import os
import logging
from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import urlparse
from scrapy.http import Request, FormRequest
from scrapy.exceptions import CloseSpider, NotConfigured
from scrapy.loader import ItemLoader
from ..items import Company
from dateutil.parser import parse
import re
from ..models import check_duplicate_article

import warnings
warnings.filterwarnings("ignore")

load_dotenv(os.path.join(Path(__file__).parent.parent.parent.parent, '.env'))


class SeekingAlphaSpider(scrapy.Spider):
    """Crawler to crawl seekingalpha earning call transcripts."""

    name = 'seekingalpha'
    allowed_domains = ['seekingalpha.com']
    handle_httpstatus_list = [404, 500]

    start_urls = ['https://seekingalpha.com']

    # Provide the websites to crawl and number of pages to crawl.
    custom_settings = {
        'earning_call_url':
            'https://seekingalpha.com/earnings/earnings-call-transcripts',
        'number_of_pages': 1}

    def start_requests(self):
        # Start web requests.

        yield Request(self.settings.get('earning_call_url'),
                      callback=self.parse_homepage,
                      meta={'number_of_pages':
                            self.settings.get('number_of_pages', 1)},
                      errback=self.err)

    def err(self, error):
        logging.error(error)

    def parse_homepage(self, response):
        # Parse homepage and extract sub-urls.

        if response.status <= 400 or response.status >= 500:

            # Extract articles from each page
            path_links = response.xpath('//@href').extract()

            path_links = [str(
                    'https://seekingalpha.com'+path_link+'?part=single')
                    for path_link in path_links if 'article' in path_link and
                    'comments_header' not in path_link and
                    'feedback' not in path_link]

            for cur_url in path_links:

                # check if the article is already present in database using
                # check_duplicate_article function and if the article is not
                # stored in database, parse it to extract details.
                report_id = None

                # extract report_id from article url
                if '-' in cur_url:
                    validation_url = cur_url
                    validation_url = validation_url.split('-')[0]
                    if '/' in validation_url:
                        report_id = int(validation_url.split('/')[-1])

                if not check_duplicate_article(report_id):
                    yield Request(url=cur_url,
                                  callback=self.parse_transcript,
                                  meta={'base_url': cur_url})

            # Extract next page.
            if response.meta['number_of_pages'] > 1:
                page_ref = response.xpath(
                        '//li[@class="next"]//@href').extract()
                if page_ref:
                    next_url = 'https://seekingalpha.com' + page_ref[0]
                    yield Request(next_url,
                                  callback=self.parse_homepage,
                                  meta={'number_of_pages':
                                        (response.meta['number_of_pages']-1)},
                                          errback=self.err)

    def parse_transcript(self, response):
        # Extract required details from each sub-page.
        # todo handle 5xx errors

        # report id
        report_link = str(response)
        if '-' in report_link:
            report_link = report_link.split('-')[0]
            if '/' in report_link:
                report_id = int(report_link.split('/')[-1])

        # company name
        article_title = response.xpath('//title/text()').extract_first()
        if '(' in article_title:
            company_name = article_title.split('(')[0].strip()

        # stock name
        stock = article_title[article_title.find("(")+1:
                              article_title.find(")")]

        # published date and quarter
        quarter_list = re.findall(r"Q\d\s\d{4}", article_title)
        if quarter_list:
            quarter = quarter_list[0]
        else:
            quarter = None

        date_published = response.xpath(
                '//div[@class="a-info clearfix"]/time/text()').extract()
        try:
            date_published = parse(date_published[0])
        except:
            date_published = None

        # article url
        article_url = response.meta['base_url']

        # audio url
        audio_call_url = None
        audio_url_text = response.xpath('//audio/source').extract()
        if audio_url_text:
            audio_call_url = re.findall(r'"([^"]*)"', audio_url_text[0])

        # company participants
        participants = ['Operator', 'Unidentified Analyst',
                        'Unidentified Company Representative']
        company_participants, participants = comp_participants(
                                              response, participants)

        # external participants
        conference_call_participants, participants = ext_participants(
                                                      response, participants)

        # Talks
        earning_call_talk = earning_call(response, participants)

        # Question and answers
        QA = qa(response, participants)

        # Load extracted items
        loader = ItemLoader(item=Company())
        loader.add_value('report_id', report_id)
        loader.add_value('company_name', company_name)
        loader.add_value('stock', stock)
        loader.add_value('published_quarter', quarter)
        loader.add_value('date_published', date_published)
        loader.add_value('earning_call_talk', earning_call_talk)
        loader.add_value('question_answers', QA)
        loader.add_value('company_participants', company_participants)
        loader.add_value('external_participants', conference_call_participants)
        loader.add_value('article_url', article_url)
        loader.add_value('article_title', article_title)
        loader.add_value('audio_call_url', audio_call_url)

        yield loader.load_item()


def comp_participants(response, participants):
        # Extract internal participants who participated in the call.

        company_participants_raw = response.xpath(
                '//div[@class="sa-art article-width"]/\
                p[contains(.,"Corporate Participants") or \
                contains(.,"Company Participants")]/\
                following-sibling::p')
        comp_participants = company_participants_raw.xpath('.//text()').\
            extract()

        company_participants = []
        if 'Conference Call Participants' in comp_participants:
            idx = comp_participants.index('Conference Call Participants')
            if idx:
                comp_participants = comp_participants[:idx]
                for participant in comp_participants:
                    if '-' in participant:
                        cur_par = participant.split(' - ')
                        company_participants.append(cur_par)
                        participants.append(cur_par[0].strip())
                    else:
                        break
        return ([company_participants], participants)


def ext_participants(response, participants):
        # collect external call participants from webpage.

        external_participants = response.xpath(
                '//div[@class="sa-art article-width"]/\
                p[contains(.,"Conference Call Participants")]/\
                following-sibling::p')

        ext_participants = external_participants.\
            xpath('.//text()').extract()

        conference_call_participants, conf_participants = [], []
        if 'Presentation' in ext_participants:
            idx = ext_participants.index('Presentation')
            if idx:
                conf_participants = ext_participants[:idx]
        elif 'Operator' in ext_participants:
            idx = ext_participants.index('Operator')
            if idx:
                conf_participants = ext_participants[:idx]
        for participant in conf_participants:
            if '-' in participant:
                cur_par = participant.split(' - ')
                conference_call_participants.append(cur_par)
                participants.append(cur_par[0].strip())
            else:
                break
        return ([conference_call_participants], participants)


def qa(response, participants):
        # Extract Question and answers during call.

        dialogs = response.xpath('//div[@class="sa-art article-width"]/\
                p[contains(.,"Question-and-Answer Session")]/\
                following-sibling::p')
        dialogs = dialogs.xpath('.//text()').extract()
        QA, cur_dialog, name = [], '', ''
        for dialog in dialogs:
            if dialog in participants:
                QA.append([name, cur_dialog])
                name = dialog
                cur_dialog = ''
            else:
                cur_dialog += (' '+dialog)
        return [QA[1:]]


def earning_call(response, participants):
        # Extract earning call details.

        ec = response.xpath(
                '//div[@class="sa-art article-width"]/\
                p[contains(.,"Operator")]/\
                following-sibling::p')
        ect = ec.xpath('.//text()').extract()
        ect_dialogs = []

        if 'Question-and-Answer Session' in ect:
            idx = ect.index('Question-and-Answer Session')
            if idx:
                ect_dialogs = ect[:idx]
        earning_call_talk, cur_dialog, name = [], '', 'Operator'

        for dialog in ect_dialogs:
            if dialog in participants:
                earning_call_talk.append([name, cur_dialog])
                name = dialog
                cur_dialog = ''
            else:
                cur_dialog += (' '+dialog)
        return [earning_call_talk]
