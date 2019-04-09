# Scrapy Crawler Starter

This is a Scrapy starter project. We try to cover the basics of Scrapy by providing an example.

## Setup
Tested with Python 3.6 via virtual environment:
```shell
$ virtualenv -p python3.6 venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

## Start Crawler

In this repo, we provide an example crawler to scrape earning call transcripts from seeking alpha website (https://seekingalpha.com/earnings/earnings-call-transcripts). See `seeking_alpha/README.md` for more information.


- Database information: we store scraped data into a local SQLite database (you can use https://sqlitebrowser.org to view the database content). To change this setting, edit the following line in `seeking_alpha_crawler/seeking_alpha_crawler/settings.py`

    ```python
    # sqlite
    SQLITE_CONNECTION_STRING = 'sqlite:///earningcall_transcripts.db' # uri of the database
    ```

- Download Limit: by default, we only crawl one page of earning call transcripts. To change this setting, change the following line `seeking_alpha_crawler/seeking_alpha_crawler/spiders/seekingalpha.py`:
    ```python
    custom_settings = {
        'earning_call_url': 'https://seekingalpha.com/earnings/earnings-call-transcripts',
        'number_of_pages': 1
    }
    ```

- Start crawler:

    ```shell
    $ cd seeking_alpha
    $ python run.py
    ```

## Crawlera (Optional)

Crawlera (https://scrapinghub.com/crawlera) is a paid proxy management service provided by ScrapingHub to avoid IP bans.

To enable Crawlera, set the following environment variables:
```
$ export CRAWLERA_ENABLED='1'
$ export CRAWLERA_APIKEY=your-api-key-from-scrapyinghub
```

## Disclaimer
The code in this repo is for learning purpose. We are not responsible for any consequences caused by any projects built using the code in this repo.
