#!/usr/bin/python
# -*- coding: utf-8 -*-
import lxml.html
import requests
import random
import click


def save_text(text, filename):
    """This method saves a text file.

    Args:
        text (str): Text to be saved in the new file.
        filename (str): Name of the new file.    
    """
    with open('{}.txt'.format(filename), 'w') as arq:
        arq.write(text)


def parse_page(url):
    """This method request the wikipedia page, get the body text and 
    all wikipedia links found.
    
    Args:
        url (str): URL to wikipedia page.
    
    Returns:
        text (str): Wikipedia body text.
        title (str): Page title or page URL in case title cannot be 
            found.
        new_urls (list): Strings list containing the URLs found in the
            page.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        page = lxml.html.fromstring(response.content)
        
        xpath = '//div[@id="bodyContent"]/descendant::p'
        # Get text of every paragraph in body div
        text = ''.join([p.text_content() for p in page.xpath(xpath)])
        # Get page title to use as filename
        page_title = page.xpath('//*[@id="firstHeading"]/text()')
        filename = (page_title[0] if page_title else url).replace('/', '')
        # Get all links to wikipedia pages in the page
        new_urls = [
            u for u in page.xpath('//a/@href') if u.startswith('/wiki/')
        ]
        return text, filename, new_urls

    except Exception as err:
        print('Error: {}'.format(err))
        return None


@click.command()
@click.option(
    '--start-url', 
    default='https://pt.wikipedia.org/wiki/Capoeira', 
    help='Wikipedia URL for starting crawler'
)
@click.option(
    '--total-files', 
    default=1000, 
    help='Max number of pages to be visited'
)
def crawler(start_url, total_files):
    root_url = start_url.split('wiki/')[0]
    urls = ['wiki/' + start_url.split('wiki/')[1]]
    visited_urls = list()
    quant_files = 0

    i = 0
    while i < len(urls) and quant_files<total_files:
        visited_urls.append(urls[i])
        page_url = root_url + urls[i]
        result_parse = parse_page(page_url)
        
        if result_parse is not None:
            text, filename, new_urls = result_parse
            save_text(text, filename)

            new_urls = [nu for nu in new_urls if nu not in visited_urls]
            urls.extend(new_urls)

        i = i + 1
        quant_files = quant_files + 1


if __name__=='__main__':
    crawler()