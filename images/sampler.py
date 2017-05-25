import os
import json
import random
import requests
from PIL import Image
from glob import glob
from text.ocr import ocr
from faces import extract_faces
from objects import extract_objects
from images.transform import resize_to_limit

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/53.0.2785.143 Chrome/53.0.2785.143 Safari/537.36'}
IMAGES_DIR = 'assets/commons'


def sample_wikicommons_urls(n):
    """sample wikicommons image urls"""
    pop = glob('assets/commons_urls/*')
    subpops = [random.choice(pop) for _ in range(n)]
    sample = []
    for p in subpops:
        choices = [l.strip() for l in open(p, 'r').readlines()]
        sample.append(random.choice(choices))
    return sample


def sample_wikicommons(n):
    """sample downloaded wikicommons images"""
    pop = glob('{}/*'.format(IMAGES_DIR))
    return random.sample(pop, min(n, len(pop)))


def download_image(url, dir, overwrite=False):
    """download an image"""
    fname = url.split('/')[-1]
    path = os.path.join(dir, fname)
    if os.path.exists(path) and not overwrite:
        return path

    res = requests.get(url, stream=True, headers=HEADERS)
    if res.status_code == 200:
        with open(path, 'wb') as f:
            for chunk in res:
                f.write(chunk)
        return path
    else:
        print('failed to download:', url)
        # res.raise_for_status()


def fetch_sample(n):
    """fetch, download, and process a sample of wikicommons image urls"""
    sample = sample_wikicommons_urls(n)
    for url in sample:
        if any(url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
            print(url)
            path = download_image(url, IMAGES_DIR)
            if path:
                # so we don't keep massive images
                try:
                    im = resize_to_limit(Image.open(path), (800, 800))
                    im.save(path)
                    extract_faces(path)
                    extract_objects(path)
                    words = ocr(path)
                    if words:
                        fname = path.split('/')[-1]
                        with open('data/words/{}.json'.format(fname), 'w') as f:
                            json.dump(words, f)
                except OSError:
                    print('unable to open:', url)
