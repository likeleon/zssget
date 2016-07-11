import sys
import argparse
import bs4
import os
import os.path
import itertools

from common import *
from urllib import request
from zipfile import ZipFile

# TODO
# --force, --output_dir, --volume, ProgressBar

__version__ = '0.5'

SITE = "http://zangsisi.net/"

class Comic():
    def __init__(self, title, url, concluded):
        self.title = title
        self.url = url
        self.concluded = concluded

def all_comics():
    soup = bs4.BeautifulSoup(get_content(SITE), 'html.parser')
    for a in soup.find(id='recent-post').find_all('a', class_='tx-link'):
        yield Comic(a.get_text(), a.get('href'), True)
    for a in soup.find(id='manga-list').find_all('a', class_='lists')[3:]:
        yield Comic(a.get_text(), a.get('href'), False)

def print_comic(comic):
    print("- title:     %s" % comic.title)
    print("  url:       %s" % comic.url)
    print("  concluded: %s" % comic.concluded)

def get_books(comic):
    soup = bs4.BeautifulSoup(get_content(comic.url), 'html.parser')
    for a in soup.find(id='recent-post').find_all('a', class_='tx-link'):
        yield a.get_text(), a.get('href')

def download(comic, output_dir='.'):
    print('Downloading %s ...' % comic.title)

    for title, link in itertools.islice(get_books(comic), 1):
        output_filename = '%s.zip' % title
        output_filepath = os.path.join(output_dir, output_filename)
        download_book(title, link, output_filepath)

def download_book(title, link, filepath):
    if os.path.exists(filepath):
        print('Skipping %s: file already exists' % (os.path.basename(filepath)))
        return
    elif not os.path.exists(os.path.dirname(filepath)):
        os.mkdir(os.path.dirname(filepath))

    with ZipFile(filepath, 'w') as zip:
        for img_url in get_image_urls(link):
            with request.urlopen(img_url) as response:
                arcname = url_basename(unquote_twice(img_url))
                zip.writestr(arcname, response.read())
    print()

def get_image_urls(link):
    soup = bs4.BeautifulSoup(get_content(link), 'html.parser')
    for img in soup.find('span', class_='contents').find_all('img'):
        yield img.get('src')

def get_parser():
    parser = argparse.ArgumentParser(description='zangsisi downloader')
    parser.add_argument('keyword', metavar='KEYWORD', type=str, nargs='*', help='keyword for searching the book by its title')
    parser.add_argument('-l', '--list', help='display all available comics', action='store_true')
    parser.add_argument('-v', '--version', help='displays the current version of zss-get', action='store_true')
    return parser

def main(**kwargs):
    sys.argv[1:] = ['은혼']

    parser = get_parser()
    args = vars(parser.parse_args())

    if args['version']:
        print(__version__)
        return

    if args['list']:
        for c in all_comics():
            print_comic(c)
        return

    if not args['keyword']:
        parser.print_help()
        return

    comics = [c for c in all_comics() if all(k in c.title for k in args['keyword'])]
    if len(comics) > 1:
        print("Ambiguous keywords: '%s'. Matched comics: " % (", ".join(keywords)))
        for c in comics:
            print_comic(c)
        return

    download(comics[0])

if __name__ == '__main__':
    main()