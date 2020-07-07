# Subreddit-Scraper

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

Use quotes if the search term is more than one world long.