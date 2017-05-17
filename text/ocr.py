import lxml
import subprocess
from collections import defaultdict


def ocr(image_path):
    """extracts words from an image,
    returning a dict of {word: [bboxes]}"""
    # run tesseract OCR
    ps = subprocess.Popen([
        'tesseract',
        image_path,
        '/tmp/result',
        'hocr',
    ])
    ps.communicate()

    with open('/tmp/result.hocr', 'r') as f:
        results = f.read()

    bboxes = defaultdict(list)
    root = lxml.html.fromstring(results.encode('utf8'))
    for word in root.cssselect('.ocrx_word'):
        text = word.text_content()
        meta = word.attrib['title'].split('; ')
        bbox = [int(v) for v in meta[0].split()[1:]]
        bboxes[text].append(bbox)
    return bboxes
