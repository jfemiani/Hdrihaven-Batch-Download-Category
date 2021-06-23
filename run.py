from tqdm import tqdm
from bs4 import BeautifulSoup
import requests
import argparse
import os

BASE_URL = "https://hdrihaven.com"
CATEGORY_URL = BASE_URL + "/hdris/category/"


def getCategories():
    content = requests.get(CATEGORY_URL).text
    soup = BeautifulSoup(content, 'html.parser')
    category_div = soup.find("div", {"class": "category-list-wrapper"})
    links = category_div.findAll("a")
    for link in links:
        url = link["href"]
        name = link.find("li").text
        yield url, name


def getImagesForCategory(url):
    url = BASE_URL + url
    content = requests.get(url).text
    soup = BeautifulSoup(content, 'html.parser')
    thumbnail_divs = soup.find("div", {"id": "item-grid"}).findAll("a")
    for i in thumbnail_divs:
        image_name = i['href'].split("h=")[1]
        yield image_name


def downloadImage(name, quality='1k', outdir='.', dry_run=False):
    url = BASE_URL + "/files/hdris/%s_%s.hdr" % (name, quality)
    if requests.head(url).status_code != 200:
        url = BASE_URL + "/files/hdris/%s_%s.exr" % (name, quality)
        if requests.head(url).status_code != 200:
             return None  # Failure
       
    
    path = os.path.join(outdir, os.path.basename(url))
    if os.path.isfile(path):
        print(f"**Skipping {name}, output file already exists")
    if not dry_run:
        response = requests.get(url, stream=True)
        with open(path, "wb") as handle:
            for data in response.iter_content():
                handle.write(data)
    return path


parser = argparse.ArgumentParser(description="A script to download all HDRIs of a certain category")
parser.add_argument("--mode", choices=['list', 'download'], help="Action to peform",  default="list")
parser.add_argument("--category_url", help="Category url (use '--mode list' to see options)", default="/hdris/category/?c=all&o=popular")
parser.add_argument("--quality", choices=["1k", "2k", "4k", "8k", "16k"], help="Quality of HDRI to download", default="8k")
parser.add_argument("--outdir", type=str, help="Output folder", default=".")
parser.add_argument("--dry-run", action="store_true", help="Do not download -- only list images")
args = parser.parse_args()

print(args)

if args.mode == "list":
    print("\n".join("%s: %s" % (name, url) for url, name in getCategories()))
else:
    os.makedirs(args.outdir, exist_ok=True)
    names = list(getImagesForCategory(args.category_url))
    for name in tqdm(names):
        path = downloadImage(name, args.quality, args.outdir, args.dry_run)
        if path is None:
            tqdm.write(f"** Bad URl: {name}")
        else:
            tqdm.write(path)
