import random
from PIL import Image
from images import annotate
from models import Screenshot
from .shot import screenshot
from .ocr import find_sequence
from .pattern import extract_patterns
from selenium.common.exceptions import TimeoutException


def extract_screenshots(articles, max_len=120):
    shots = [extract_screenshot(a, max_len) for a in articles]
    return [s for s in shots if s is not None]


def extract_screenshot(article, max_len):
    patterns = [p for p in extract_patterns(article) if len(p) < max_len]
    if not patterns:
        return
    try:
        screenshot(article['url'], '/tmp/shot.png')
    except TimeoutException:
        return
    random.shuffle(patterns)
    while patterns:
        pat = patterns.pop()
        # try to find bbox seq that matches the pattern
        bboxes = find_sequence('/tmp/shot.png', pat.split())
        if bboxes:
            img = Image.open('/tmp/shot.png')
            for bbox in bboxes:
                img = annotate.underline_and_crop_bbox(img, bbox)
            return Screenshot(img)
    return
