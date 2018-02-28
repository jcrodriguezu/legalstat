# -*- coding: utf-8 -*-
"""Legal start web scraper test."""

import json
import argparse
import requests
import lxml.html

from scraper import ItemParser, Scraper

INITIAL_URL = "https://yolaw-tokeep-hiring-env.herokuapp.com/"


class WebScraper(object):
    """LegalStart web scraper."""
    
    _initial_action = 0

    def process(self, json_path, initial_url=INITIAL_URL, location="local"):
        """process the data.
        :param json_path, String
        :param initial_url, String
        :param location, String
        """
        rules = self.__get_local_json_data(json_path)
        item_parser = ItemParser(rules[str(self._initial_action)])
        scraper = Scraper(auth="auth", user="Thumb", 
                          passw="Scraper", 
                          initial_url=initial_url)
        response = scraper.start_request()
        current_page = self._initial_action

        while True:
            scraped_item = scraper.parse_item(response, item_parser)
            if scraped_item is None:
                print("ALERT - Can’t move to page {prev_page}: page {current_page} link has been malevolently tampered with!!".format(
                    prev_page=item_parser.get_next_parser(), current_page=current_page
                ))
                break

            print ("Move to page {current_page}".format(current_page=current_page))
            next_parser = scraped_item['next_parser']
            next_url = scraped_item['next_url']

            item_parser = ItemParser(rules[next_parser])
            response = scraper.start_request(url=next_url)
            current_page = next_parser

    def get_json_data(self, json_path, location):
        if location == 'web':
            return self.__get_remote_json_data(json_path)
        return self.__get_local_json_data(json_path)
    
    def __get_local_json_data(self, json_path):
        with open(json_path) as js_data:
            return json.load(js_data)

    def __get_remote_json_data(self, json_path):
        pass


def get_parameters():
    """Check the script parameters and return a dict with the values.
    
    :return: Dict with the parsed parameters. Ex:
        {
            json_path: /home/user/test/test.json,
            location: web
        }
    """
    parser = argparse.ArgumentParser(
        prog='python web_scraper.py', description='web scraper test for legal start.')
    parser.add_argument('json_path', help='Path to the json file')
    parser.add_argument('-l', '--location', choices=["web", "local"], 
                        help='If the path is a local file or a web url',
                        required=True)
    parser.add_argument('-i', '--initial_url', help="Initial url", 
                        default=INITIAL_URL)

    args = parser.parse_args()
    return vars(args)


if __name__ == "__main__":
    params = get_parameters()
    WebScraper().process(**params)
