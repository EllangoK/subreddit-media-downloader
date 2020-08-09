# -*- coding: utf-8 -*-

from skimage.metrics import structural_similarity as ssim
from imgurpython import ImgurClient
from collections import defaultdict
from psaw import PushshiftAPI
from bs4 import BeautifulSoup
from tqdm import tqdm
import urllib.request
import configparser
import numpy as np
import requests
import shutil
import time
import cv2
import sys
import re
import os

help_message = """
Easily download a subreddit's images and videos

Format:
    $ python subreddit_download.py <subreddit> <search term>
    or
    $ python subreddit_download.py <subreddit> <search term> <upvote threshold>

Example:
    $ python subreddit_download.py pics cat

Files are saved to a folder with the same name as the search term.
If you omit the upvote threshold, a praw.ini file will not be required
If you want to download nsfw albums, fill out the imgur.ini file
Thus, images and videos can be gathered without authentication

Use quotes if more than one word
"""
omitted = []

def load_imgur_client(ini_file):
    config = configparser.ConfigParser()
    try:
        config.read(ini_file)
        data = config['imgur']
        return ImgurClient(data['client_id'], data['client_secret']) if '' not in [data['client_id'], data['client_secret']] else None
    except:
        return None

client = load_imgur_client('imgur.ini')

def nsfw_links_from_album(url):
    album_key = url.split('a/')[-1] if '/a/' in url else url.split('gallery/')[-1]
    links = [item.link for item in client.get_album_images(album_key)]
    return links if links else None

def threshold(data, upvote_thresh):
    return [item for item in data if int(item[3]) > upvote_thresh]

def gfycat_source(url):
    if 'giant' in url:
        return None
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    try:
        return [item.get('src') for item in list(soup.find_all("source")) if item.get('src') is not None and 'mobile' not in item.get('src') and 'webm' in item.get('src')][0]
    except:
        return None

def imgur_album_source(url):
    album_key = url.split(
        'a/')[-1] if '/a/' in url else url.split('gallery/')[-1]
    soup = BeautifulSoup(requests.get(
        "http://imgur.com/a/" + album_key + "/layout/blog").content, 'html.parser')
    ids = list(set(re.findall(
        '.*?{"hash":"([a-zA-Z0-9]+)".*?"ext":"(\.[a-zA-Z0-9]+)".*?', soup.prettify())))
    links = []
    for item in ids:
        links.append("https://i.imgur.com/" + ''.join(item))
    if len(ids) == 0:
        return url
    return links

def source_url(link):
    if '?' in link:
        link = link.split('?')[0]
    if link.endswith('.gifv'):
        link = link[:-1]
    if any(item in link for item in ['gfycat', 'gifdeliverynetwork', 'redgifs']):
        link = gfycat_source(link)
    elif '/imgur.com' in link and not any(item in link for item in ['/a/', '/gallery/']):
        link = link.replace('imgur', 'i.imgur') + '.jpg'
    elif '/imgur.com' in link and any(item in link for item in ['/a/', '/gallery/']):
        link = imgur_album_source(link) #If it is a nsfw album, it returns itself else a list of link
        if any(item in link for item in ['/a/', '/gallery/']) and client:
            link = nsfw_links_from_album(link)
    elif any(link.endswith(item) for item in ['.gif', '.mp4', '.webm', '.jpg', '.jpeg', '.png']):
        link = link
    return link

def download_images(folder_name, file_names_and_download_links):
    folder_name = os.path.join(os.getcwd(), folder_name)
    if os.path.isdir(folder_name) and not os.listdir(folder_name):
        shutil.rmtree(folder_name)
    os.mkdir(folder_name)

    for item in tqdm(file_names_and_download_links):
        if item[1] == None:
            continue
        if item[1] is not None and 'thcf' in item[1]:
            downloaded = False
            for i in range(0, 10):
                try:
                    urllib.request.urlretrieve(
                        item[1], folder_name + '\\' + item[0])
                    downloaded = True
                    break
                except:
                    item[1] = item[1].replace(
                        item[1][item[1].find('thcf')+4], str(i))
                    continue
            if not downloaded:
                omitted.append((item[1], item[0]))
        else:
            try:
                urllib.request.urlretrieve(item[1], folder_name + '\\' + item[0])
            except:
                omitted.append((item[1], item[0]))
                continue
    return folder_name

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
    for submission in tqdm(r.info(fullnames), total=len(fullnames)):
        info = [submission.id, submission.title,
                submission.url, submission.score]
        if None not in info:
            useful_info.append(info)
        else:
            continue
    return useful_info


def merge_common(lists):
    neigh = defaultdict(set)
    visited = set()
    for each in lists:
        for item in each:
            neigh[item].update(each)

    def comp(node, neigh=neigh, visited=visited, vis=visited.add):
        nodes = set([node])
        next_node = nodes.pop
        while nodes:
            node = next_node()
            vis(node)
            nodes |= neigh[node] - visited
            yield node
    for node in neigh:
        if node not in visited:
            yield sorted(comp(node))


def keep_widest_img(data):
    widest_file = max(data, key=lambda i: i[0])
    for item in data:
        if item[1] == widest_file[1]:
            continue
        else:
            os.remove(item[1])


def keep_highest_name(data):
    num_filenames = [(item[1].split('/')[-1].split(',')[0], item[1])
                     for item in data]
    highest_filename = max(num_filenames, key=lambda i: int(i[0]))
    widest_file = max(data, key=lambda i: int(i[0]))
    img = cv2.imread(widest_file[1])
    for item in data:
        os.remove(item[1])
    cv2.imwrite(highest_filename[1], img)


def mse(first_img, second_img):
    err = np.sum((first_img.astype("float") - second_img.astype("float")) ** 2)
    err /= float(first_img.shape[0] * first_img.shape[1])
    return err


def dhash(image, hashSize=8):
    resized_img = cv2.resize(image, (hashSize + 1, hashSize))
    diff = resized_img[:, 1:] > resized_img[:, :-1]
    return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])


def dhash_path(path, hashSize=8):
    if path.endswith(".webm") or path.endswith(".mp4") or path.endswith(".gif"):
        return None
    image = cv2.imread(path, 0)
    if image is None:
        return None
    return dhash(image, hashSize=hashSize)


def remove_duplicates(directory, custom=True):
    image_data = {}
    pic_hashes = {}

    print("Calculating dhashes")
    for rel_path in tqdm(os.listdir(directory)):
        path = directory + "/" + rel_path
        img = cv2.imread(path, 0)
        if img is None:
            continue
        image_data[path] = [img, cv2.resize(
            img, (8, 8), interpolation=cv2.INTER_AREA), img.shape[1]]
        image_hash = dhash(img)
        if image_hash is None:
            continue
        elif image_hash in pic_hashes:
            pic_hashes[image_hash].append(path)
        else:
            pic_hashes[image_hash] = [path]

    dupe_list = []
    for key in pic_hashes.keys():
        if len(pic_hashes[key]) > 1:
            dupe_list.append(pic_hashes[key])

    if len(dupe_list) == 0:
        print("No Duplicates Found via Dhash")
    else:
        count = 0
        for i in dupe_list:
            for j in i:
                count += 1
        count -= len(dupe_list)

        print("Deleting " + str(count) + " dupes found via Dhash")
        for dupes in tqdm(dupe_list):
            data = [(image_data[path][2], path) for path in dupes]
            if custom:
                keep_highest_name(data)
            else:
                keep_widest_img(data)

    paths = [directory + "/" + item for item in os.listdir(directory)]
    for key in image_data:
        if key not in paths:
            image_data[key] = None

    dupe_list = []
    print("Calculating MSE and SSIM")
    for data in tqdm(image_data):
        mse_ssim = [(key, mse(image_data[data][1], image_data[key][1]), ssim(image_data[data][1], image_data[key][1]))
                    for key in image_data if data is not key and image_data[data] is not None and image_data[key] is not None]
        dupe = [item[0]
                for item in mse_ssim if item[2] > 0.9 and item[1] < 5]
        if dupe != []:
            dupe.insert(0, data)
            dupe_list.append(dupe)
    dupe_list = list(merge_common(dupe_list))

    if len(dupe_list) == 0:
        print("No Duplicates Found")
        sys.exit()
    else:
        count = 0
        for i in dupe_list:
            for j in i:
                count += 1
        count -= len(dupe_list)

        print("Deleting " + str(count) + " dupes found via SSIM and MSE")
        for dupes in tqdm(dupe_list):
            data = [(image_data[path][2], path) for path in dupes]
            if custom:
                keep_highest_name(data)
            else:
                keep_widest_img(data)

def generate_file_names_and_download_links(pushshift_results, upvote_thresh):
    file_names_and_download_links = []
    if not upvote_thresh:
        information = pushshift_based(pushshift_results)
        print("Gathering " + str(len(information)) + " Source Links")
        for item in tqdm(information):
            source_link = source_url(item[2])
            if isinstance(source_link, list):
                for index, link in enumerate(source_link):
                    #Id - Index . Extension
                    file_names_and_download_links.append([str(item[0]) + '-' + str(index) + '.' +
                                                          str(link).split('.')[-1], link])
            else:
                #Id . Extension
                file_names_and_download_links.append([str(item[0]) + '.' +
                                                      str(source_link).split('.')[-1], source_link])
        print("Downloading " + str(len(file_names_and_download_links)) + " Images")
    else:
        print("Gathering Upvote Data")
        information = threshold(praw_based(pushshift_results), upvote_thresh)
        print("Gathering " + str(len(information)) +
              " Source Links out of a possible " + str(len(pushshift_results)) + " Links")
        for item in tqdm(information):
            source_link = source_url(item[2])
            if isinstance(source_link, list):
                for index, link in enumerate(source_link):
                    #Upvote , Id - Index . Extension
                    file_names_and_download_links.append([str(item[3]) + ',' + str(item[0]) + '-' + str(index) + '.' +
                                                          str(link).split('.')[-1], link])
            else:
                #Upvote , Id . Extension
                file_names_and_download_links.append([str(item[3]) + ',' + str(item[0]) + '.' +
                                                      str(source_link).split('.')[-1], source_link])
        print("Downloading " + str(len(file_names_and_download_links)) +
              " Images out of a possible " + str(len(pushshift_results)) + " Images")
    return file_names_and_download_links

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
          '" ' + "on " + ', '.join(['r/' + i for i in args[0].split(',')]) + " for images and videos", end='')
    
    if upvote_thresh:
        print(" with an upvote threshold of " + args[2])

    pushshift_results = []
    for item in args[0].split(','):
        pushshift_results.extend(search_pushshift(item, args[1]))

    if len(pushshift_results) == 0:
        print("No results found. Check to make sure your properly spelled the subreddit name and search term")
    
    file_names_and_download_links = generate_file_names_and_download_links(
        pushshift_results, upvote_thresh)
    folder = download_images(args[1], file_names_and_download_links)

    if len(omitted):
        print("These links are broken or can't be downloaded: " + str(omitted))

    remove_duplicates(folder)
