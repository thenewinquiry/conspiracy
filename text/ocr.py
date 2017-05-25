import lxml.html
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
    seq = []
    for word in root.cssselect('.ocrx_word'):
        text = word.text_content()
        meta = word.attrib['title'].split('; ')
        bbox = [int(v) for v in meta[0].split()[1:]]
        bboxes[text].append(bbox)
        seq.append((text, bbox))
    return bboxes, seq


def find_sequence(image_path, terms):
    """attempt to find a sequence of bounding boxes
    matching a sequence of terms"""
    _, seq = ocr(image_path)

    bboxes = []
    queue = terms
    for term, bbox in seq:
        if not queue:
            break
        if term == queue[0]:
            queue.pop(0)
            bboxes.append(bbox)
        else:
            # reset
            bboxes = []
            queue = terms
    if len(bboxes) != len(terms):
        return []
    return bboxes
