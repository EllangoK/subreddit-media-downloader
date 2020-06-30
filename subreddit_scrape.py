import urllib.request
import json
from psaw import PushshiftAPI
import praw

api = PushshiftAPI()
r = praw.Reddit('bot1')

psaw_search = list(api.search_submissions(q='search', subreddit='subreddit',
                                          filter=['id', 'author',
                                                  'title', 'upvotes'],
                                          limit=10000))

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
    if item[3] not in [item[3] for item in not_duplicates] or item[1] not in [item[1] for item in not_duplicates]:
        not_duplicates.append(item)
len(not_duplicates)


for (idx, item) in enumerate(not_duplicates):
    print(item[3], 'C:\\img\\' + str(item[1]) + '.' + str((item[3])[-3:]))
    try:
        urllib.request.urlretrieve(item[3], 'C:\\img\\' + str(item[2]) + ',' + str(idx) + str((item[3])[-4:]))
    except:
        pass
