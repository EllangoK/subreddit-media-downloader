# Subreddit-Media-Downloader

Easily download a subreddit's images and videos

Format:

	$ python subreddit_download.py <subreddit> <search term>

or

	$ python subreddit_download.py <subreddit> <search term> <upvote threshold>

Example:

	$ python subreddit_download.py pics cat

Files are saved to a folder with the same name as the search term.
If you omit the upvote threshold, a praw.ini file will not be required
Thus, images and videos can be gathered without authentication

Use quotes if the search term is more than one world long.