import requests
import lxml.html
from urllib.parse import urlparse


class Scraper(object):
    
    initial_url = "https://yolaw-tokeep-hiring-env.herokuapp.com/"

    def __init__(self, *args, **kwargs):
        if 'auth' in kwargs:
            self.auth = (kwargs['user'], kwargs['passw'])

        if 'initial_url' in kwargs:
            self.initial_url = kwargs['initial_url']

    def start_request(self, url=None):
        if url:
            return requests.get(url, auth=self.auth)
        else:
            return requests.get(self.initial_url, auth=self.auth)

    def parse_item(self, response, item_parser):
        item = {}
        
        if not item_parser:
            raise Exception("item_parser is required")

        raw_html = lxml.html.fromstring(response.content)
        if not item_parser.is_valid(raw_html):
            return None

        base_url = self.__get_base_url(response)
        item['next_url'] = item_parser.get_next_url(raw_html, base_url=base_url)
        item['next_parser'] = item_parser.get_next_parser()
        return item

    def __get_base_url(self, response):
        parsed_url = urlparse(response.url)
        return "{uri.scheme}://{uri.netloc}".format(uri=parsed_url)


class ItemParser(object):
    
    def __init__(self, rules):
        self.rules = rules

    def get_test_query(self, raw_html):
        return raw_html.xpath(self.rules['xpath_test_query'])

    def is_valid(self, raw_html):
        expected = self.rules['xpath_test_result']
        result = self.get_test_query(raw_html)
        return result == expected

    def get_next_url(self, raw_html, base_url=None):
        xpath = self.rules['xpath_button_to_click']
        link_url = "{0}/@href".format(xpath)
        next_url = raw_html.xpath(link_url)[0]
        if base_url and base_url not in next_url:
            next_url = "{0}/{1}".format(
                base_url.rstrip("/"), 
                next_url.lstrip("/"))
        return next_url

    def get_next_parser(self):
        return self.rules['next_page_expected']
        