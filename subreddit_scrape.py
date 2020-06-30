#!/usr/bin/python3
# -*- coding: utf-8 -*-

from psaw import PushshiftAPI
from bs4 import BeautifulSoup
import urllib.request
import requests
import shutil
import math
import time
import sys
import os

help_message = """
Easily scrape a subreddit for its images and videos

Format:
    $ python subreddit_scrape.py <subreddit> <search term>
    or
    $ python subreddit_scrape.py <subreddit> <search term> <upvote threshold>

Example:
    $ python subreddit_scrape.py pics cat

Files are saved to a folder with the same name as the search term.
If you omit the upvote threshold, a praw.ini file will not be required
Thus, images and videos can be gathered without authentication

Use quotes if more than one word
"""
omitted = []

def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 *
                                                     (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)

    if iteration == total:
        print()

def threshold(data, upvote_thresh):
    return [item for item in data if int(item[3]) > upvote_thresh]

def gfycat_source(url):
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    try:
        return [item.get('src') for item in list(soup.find_all("source")) if item.get('src') is not None and 'mobile' not in item.get('src') and 'mp4' in item.get('src')][0]
    except:
        return None

def ensure_gfycat(url):
    if url == None:
        return url
    for i in range(0,10):
        try:
            urllib.request.urlopen(url).getcode()
            return url
        except:            
            url = url.replace(url[url.find('thcf')+4], str(i))

def source_url(link):
    if '?' in link:
        link = link.split('?')[0]
    if link.endswith('.gifv'):
        link = link[:-1]
    if any(item in link for item in ['gfycat', 'gifdeliverynetwork', 'redgifs']):
        link = ensure_gfycat(gfycat_source(link))
    elif '/imgur.com' in link and not any(item in link for item in ['/a/', '/gallery/']):
        link = link.replace('imgur', 'i.imgur') + '.jpg'
    elif any(link.endswith(item) for item in ['.gif', '.mp4', '.webm', '.jpg', '.jpeg', '.png']):
        link = link
    return link

def download_images(folder_name, file_names_and_download_links):
    folder_name = os.path.join(os.getcwd(), folder_name)
    if os.path.isdir(folder_name):
        shutil.rmtree(folder_name)
    os.mkdir(folder_name)

    printProgressBar(0, len(file_names_and_download_links), prefix='Progress:',
                     suffix='Complete', length=60)
    for i, item in enumerate(file_names_and_download_links):
        printProgressBar(i + 1, len(file_names_and_download_links), prefix='Progress:',
                         suffix='Complete', length=60)
        if item[1] is not None and 'thcf' in item[1]:
            downloaded = False
            while not downloaded:
                try:
                    urllib.request.urlretrieve(item[1], folder_name + '\\' + item[0])
                    downloaded = True
                except:
                    continue
        else:
            try:
                urllib.request.urlretrieve(item[1], folder_name + '\\' + item[0])
            except:
                omitted.append(item[1])
                continue

def search_pushshift(subreddit_name, search_term):
    api = PushshiftAPI()
    psaw_search = list(api.search_submissions(q=search_term, subreddit=subreddit_name,
                                            filter=['id', 'author',
                                                    'title', 'url'],
                                            limit=5000))
    
    return [item for item in psaw_search if 'reddit.com/r/' not in item[4]]

def pushshift_based(results):
    useful_info = [item[2:5] for item in results if None not in item[2:5]]
    return useful_info

def praw_based(results):
    import praw
    r = praw.Reddit('bot1')
    fullnames = []
    for id in [i[2] for i in results]:
        fullnames.append('t3_' + id)

    useful_info = []
    printProgressBar(0, len(fullnames), prefix='Progress:',
                     suffix='Complete', length=60)
    for i, submission in enumerate(r.info(fullnames)):
        info = [submission.id, submission.title,
                submission.url, submission.score]
        printProgressBar(i + 1, len(fullnames), prefix='Progress:',
                         suffix='Complete', length=60)
        if None not in info:
            useful_info.append(info)
        else:
            continue
    return useful_info

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

    print("Searching for" + ' "' + args[1] +
          '" ' + "on r/" + args[0] + " for images and videos", end='')
    if upvote_thresh:
        print(" with an upvote threshold of " + args[2])
    else:
        print()
    pushshift_results = search_pushshift(args[0], args[1])

    if len(pushshift_results) == 0:
        print("No results found. Check to make sure your properly spelled the subreddit name and search term")

    if not upvote_thresh:
        information = pushshift_based(pushshift_results)

        print("Gathering " + str(len(information)) + " Source Links")
        printProgressBar(0, len(information), prefix='Progress:',
                        suffix='Complete', length=60)
                        
        file_names_and_download_links = []
        for i, item in enumerate(information):
            source_link = source_url(item[2])
            file_names_and_download_links.append((str(item[0]) + '.' +
                                                  str(source_link).split('.')[-1], source_link))
            printProgressBar(i + 1, len(information),
                             prefix='Progress:', suffix='Complete', length=60)

        print("Downloading " + str(len(file_names_and_download_links)) + " Images")
        download_images(args[1], file_names_and_download_links)
    else:
        print("Gathering Upvote Data")
        information = threshold(praw_based(pushshift_results), upvote_thresh)

        print("Gathering " + str(len(information)) +
              " Source Links out of a possible " + str(len(pushshift_results)) + " Links")
        printProgressBar(0, len(information), prefix='Progress:',
                         suffix='Complete', length=60)

        file_names_and_download_links = []
        for i, item in enumerate(information):            
            source_link = source_url(item[2])
            file_names_and_download_links.append((str(item[3]) + ',' + str(item[0]) + '.' +
                                                 str(source_link).split('.')[-1], source_link))
            printProgressBar(i + 1, len(information),
                             prefix='Progress:', suffix='Complete', length=60)

        print("Downloading " + str(len(file_names_and_download_links)) + " Images out of a possible " + str(len(pushshift_results)) + " Images")
        download_images(args[1], file_names_and_download_links)
    print(omitted)
