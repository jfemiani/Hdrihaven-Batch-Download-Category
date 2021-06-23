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


def downloadImage(name, quality):
    url = BASE_URL + "/files/hdris/%s_%s.hdr" % (name, quality)
    response = requests.get(url, stream=True)
    path = os.path.join(outdir, name + ".hdr")
    with open(path, "wb") as handle:
        for data in response.iter_content():
            handle.write(data)


parser = argparse.ArgumentParser(description="A script to download all HDRIs of a certain category")
parser.add_argument("--mode", choices=['list', 'download'], help="Action to peform",  default="list")
parser.add_argument("--category_url", help="Category url (use '--mode list' to see options)", default="/hdris/category/?c=all&o=popular")
parser.add_argument("--quality", choices=["1k", "2k", "4k", "8k", "16k"], help="Quality of HDRI to download", default="8k")
parser.add_argument("--outdir", type=str, help="Output folder", default=".")
cmd = parser.parse_args()


if cmd.mode == "list":
    print("\n".join("%s: %s" % (name, url) for url, name in getCategories()))
else:
    os.makedirs(args.outdir, exist_ok=True)
    for name in tqdm(getImagesForCategory(cmd.category_url)):
        downloadImage(name, cmd.quality, args.outdir)
