#!/usr/bin/python
# -*- coding: utf-8 -*-

from psaw import PushshiftAPI
import praw

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

r = praw.Reddit('bot1')

fullnames = []
for id in [i[2] for i in psaw_search]:
    fullnames.append('t3_' + id)

useful_info = []
for submission in r.info(fullnames):
    b = [submission.id, submission.title, submission.score,
         submission.url]
    useful_info.append(b)

threshold = [item for item in useful_info if int(item[2]) > 300]
len(threshold)

not_duplicates = []
for item in threshold:
    print item
    if item[3] not in [item[3] for item in not_duplicates] or item[1] \
            not in [item[1] for item in not_duplicates]:
        not_duplicates.append(item)
len(not_duplicates)


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

def search_pushshift(subreddit_name, search_term):
    api = PushshiftAPI()
    psaw_search = list(api.search_submissions(q=search_term, subreddit=subreddit_name,
                                            filter=['id', 'author',
                                                    'title', 'upvotes'],
                                            limit=10000))

    return [item for item in psaw_search if 'reddit.com/r/' not in item[4]]

def pushshift_only(results):
    name_and_url = [item[3:5] for item in results]
    return name_and_url

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
        pushshift_only(pushshift_results)
