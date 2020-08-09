# Subreddit-Media-Downloader

Easily download a subreddit's images and videos without authentication

Format:

	$ python subreddit_download.py <subreddit> <search term>

Example:

	$ python subreddit_download.py pics cat

Files are saved to a folder with the same name as the search term.

Thus, images and videos can be gathered without authentication

Use quotes if the search term is more than one world long.

## Advanced Usage

### Upvote Thresholding

Format:

	$ python subreddit_download.py <subreddit> <search term> <upvote threshold>

To only download posts above a certain amount of upvotes, a praw.ini file is required.

The praw.ini follows the formated layed out in the [PRAW Docs](https://praw.readthedocs.io/en/latest/getting_started/configuration/prawini.html)

If the file is not present and upvote thresholding is passed in as an arguement, the program will fail.

### Restricted Imgur Albums

To download restricted imgur albums, for example NSFW ones, a imgur.ini file is required.

There is no standard format so instead fill out the template imgur.ini file.

Client ID and Secret can be found/created in your [Imgur account settings](https://imgur.com/account/settings/apps)

If the file is empty or not present, the program will still run regardless.
