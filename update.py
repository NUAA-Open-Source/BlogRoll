#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import miniflux
import mistune
import os
import pprint
import requests

from mistune.plugins.table import table


markdown = mistune.create_markdown(renderer='ast', plugins=[table])


def format_rss(blogroll_url):
    table_line = []
    rss_urls = []
    checked_rss_urls = []

    r = requests.get(blogroll_url)
    ast = markdown(r.text)

    for elem in ast:
        if isinstance(elem, dict) and elem['type'] == 'table':
            for tbl_elem in elem['children']:
                if tbl_elem['type'] == "table_body":
                    for line_elem in tbl_elem['children']:
                        table_line.append(line_elem['children'][2])
    for elem in table_line:
        raw_data: str = elem['children'][0]['raw']
        if raw_data.startswith("http"):
            rss_urls.append(raw_data)

    pprint.pp(rss_urls)

    for url in rss_urls:
        print("getting {}".format(url))
        try:
            req = requests.get(url)
            if req.status_code != 200:
                print(f"{url} with status code {req.status_code}")
                continue
            if req.text.startswith("<?xml"):
                checked_rss_urls.append(url)
        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
            print(f"{url} with exception {e}")
            continue
        except Exception as e:
            print(f"{url} failed with exception {e}")
            continue

    return checked_rss_urls


def add_client(valid_rss, client):
    for url in valid_rss:
        try:
            feed_id = client.create_feed(url, category_id=3, crawler=True)
            print(feed_id)
        except (miniflux.BadRequest, miniflux.ServerError) as e:
            print(f"{url} with exception {e}!")
            continue


def get_current_status(client: miniflux.Client):
    feeds = [(feed['title'], feed['site_url']) for feed in client.get_feeds()]
    pprint.pp(feeds)


if __name__ == '__main__':

    miniflux_endpoint = os.environ["MINIFLUX_ENDPOINT"]
    miniflux_api_key = os.environ["MINIFLUX_API_KEY"]
    blogroll_url = "https://raw.githubusercontent.com/NUAA-Open-Source/BlogRoll/master/README.md"

    client = miniflux.Client(miniflux_endpoint, api_key=miniflux_api_key)

    valid_rss = format_rss(blogroll_url)
    add_client(valid_rss, client)
    get_current_status(client)
