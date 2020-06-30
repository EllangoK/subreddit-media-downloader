#!/usr/bin/python
# -*- coding: utf-8 -*-

from psaw import PushshiftAPI
from bs4 import BeautifulSoup
import requests
import sys

import urllib.request

help_message = """
Easily scrape a subreddit for its images and videos

Format:
    $ python subreddit_scrape.py <subreddit> <search term>
    or
    $ python subreddit_scrape.py <subreddit> <search term> <upvote threshold>

Example:
    $ python subreddit_scrape.py pics cat

If you omit the upvote threshold, a praw.ini file will not be required
Thus, images and videos can be gathered without authentication

Use quotes if more than one word
"""

'''
for (idx, item) in enumerate(not_duplicates):
    print(item[3],
          'C:\\img\\'
          + str(item[1]) + '.' + str((item[3])[-3:]))
    try:
        urllib.request.urlretrieve(item[3], 
                                    'C:\\img\\'
                                    + str(item[2]) + ',' + str(idx)
                                    + str((item[3])[-4:]))
    except:
        pass
'''

def threshold(data, upvote_thresh):
    return [item for item in data if int(item[3]) > upvote_thresh]

def gfycat_source(url):
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    return [item.get('src') for item in list(soup.find_all("source")) if item.get('src') is not None and 'mobile' not in item.get('src') and 'mp4' in item.get('src')][0]

def source_url(link):
    if '?' in link:
        link = link.split('?')[0]
    if link.endswith('.gifv'):
        link = link[:-1]
    url = None
    if any(item in link for item in ['gfycat', 'gifdeliverynetwork', 'redgifs']):
        url = gfycat_source(link)
    elif '/imgur.com' in link and not any(item in link for item in ['/a/', '/gallery/']):
        url = link.replace('imgur', 'i.imgur') + '.jpg'
    elif any(link.endswith(item) for item in ['.gif', '.mp4', '.webm', '.jpg', '.jpeg', '.png']):
        url = link

def search_pushshift(subreddit_name, search_term):
    api = PushshiftAPI()
    psaw_search = list(api.search_submissions(q="Azula", subreddit="rule34",
                                            filter=['id', 'author',
                                                    'title', 'url'],
                                            limit=10000))

    return [item for item in psaw_search if 'reddit.com/r/' not in item[4]]

def pushshift_based(results):
    useful_info = [item[2:5] for item in results]
    return useful_info

def praw_based(results):
    import praw
    r = praw.Reddit('bot1')
    fullnames = []
    for id in [i[2] for i in results]:
        fullnames.append('t3_' + id)

    useful_info = []
    for submission in r.info(fullnames):
        useful_info.append([submission.id, submission.title,
                            submission.url, submission.score])

if __name__ == '__main__':
    args = sys.argv[1:]
    upvote_thresh = 0

    if len(args) < 2 or len(args) > 3:
        print(help_message)
        sys.exit()
    if len(args) == 3:
        try:
            upvote_thresh = int(args[2])
        except:
            print("Error: Upvote threshold is not an integer")
            sys.exit()
    
    pushshift_results = search_pushshift(args[0], args[1])
    if len(pushshift_results) == 0:
        print("No results found. Check to make sure your properly spelled the subreddit name and search term")

    if not upvote_thresh:
        information = pushshift_based(pushshift_results)
    else:
        information = threshold(praw_based(pushshift_results), upvote_thresh)

