import json
import random
import hashlib
import numpy as np
from glob import glob
from PIL import Image, ImageDraw
from faces import compare_faces
from itertools import chain
from images import util, layout, compare, annotate
from text import shot, ocr

SAMPLE = 200
SIZE = (1400, 800)
MAX_SIZE = (0.3, 0.3)
MAX_SIZE = (MAX_SIZE[0]*SIZE[0], MAX_SIZE[1]*SIZE[1])
COLORS = [(255,0,0), (0, 100, 255), (6, 214, 44), (242, 226, 4)]
images = random.sample(glob('../reality/data/_images/*'), SAMPLE)
ENTS = ['ORG', 'GPE', 'NORP', 'PERSON', 'EVENT' , 'WORK_OF_ART']



def hash(text):
    return hashlib.md5(text.encode('utf8')).hexdigest()


def lookup_article(imid):
    # ugh no reverse lookup, brute force search for now
    files = glob('../reality/data/**/*.json')
    for path in files:
        data = json.load(open(path, 'r'))
        for a in data:
            if hash(a['image']) == imid:
                return a


def load_images(impath, type):
    """load images given a parent image path"""
    imid = impath.split('/')[-1]
    dir = 'data/{}/{}'.format(type, imid)
    try:
        bboxes = json.load(open('{}/bboxes.json'.format(dir), 'r'))
        crops = glob('{}/*.jpg'.format(dir))
        return [{
            'path': c,
            'bbox': b,
            'imid': imid,
            'impath': impath
        } for c, b in zip(crops, bboxes)]
    except FileNotFoundError:
        return []


def filter_pairs(pairs, images):
    """filters redundant image pairs"""
    # remove permutations
    pairs = set(tuple(sorted(p)) for p in pairs)

    # filter out self-pairings
    # filter out pairs that are between two of the same images
    # filter out pairs that are from really similar images
    pairs = [(a, b) for a, b in pairs
             if a != b
             and images[a]['imid'] != images[b]['imid']
             and compare.compute_dist(images[a]['impath'], images[b]['impath']) >= 20]
    return pairs


def get_similar(images, thresh, comparator, prefix=None):
    """get pairs of similar images,
    according to the comparator (distance) function"""
    dists = comparator([i['path'] for i in images])
    pairs = np.argwhere(dists <= thresh)
    pairs = filter_pairs(pairs, images)

    # get unique dist mat indices
    indices = set(chain(*pairs))
    images = {idx: images[idx] for idx in indices}

    if prefix is not None:
        # since indices can collide, add prefixes
        pairs = [
            ('{}{}'.format(prefix, a), '{}{}'.format(prefix, b))
            for a, b in pairs]
        images = {'{}{}'.format(prefix, k): v for k, v in images.items()}
    return pairs, images


def prepare_images(images):
    """prepare images by loading and scaling them,
    scaling their bounding boxes accordingly"""
    for image in images.values():
        im = Image.open(image['impath'])
        xo, yo = im.size

        im = util.resize_to_limit(im, MAX_SIZE)
        xn, yn = im.size

        resize_ratio = (xn/xo, yn/yo)

        # scale bbox accordingly
        image['bbox'] = util.scale_rect(image['bbox'], resize_ratio)
        image['image'] = im
    return images


def render(images, pairs, out='output.jpg', shakiness=30):
    """collages the images, annotating similar pairs by drawing links"""
    canvas = Image.new('RGB', SIZE, color=0)
    draw = ImageDraw.Draw(canvas)

    # get articles
    articles = [lookup_article(im['imid']) for im in images.values()]
    articles = random.sample(articles, min(len(articles), 4))
    texts = []
    for a in articles:
        ents = [e.strip() for e, typ in a['entities'] if typ in ENTS and len(e) > 1]
        ent = random.choice(ents)
        shot.screenshot(a['url'], '/tmp/shot.png')
        words = ocr.ocr('/tmp/shot.png')
        bboxes = words.get(ent, [])
        if bboxes:
            bbox = random.choice(bboxes)
            img = Image.open('/tmp/shot.png')
            img = annotate.underline_and_crop_bbox(img, bbox)
            texts.append({
                'image': img
            })

    vals = list(images.values()) + texts
    random.shuffle(vals)
    ims = [im['image'] for im in vals]

    # layout images
    # this doesn't guarantee that every image will be included!
    packed = layout.pack(ims, canvas)
    for im, pos in zip(vals, packed):
        pos = (
            round(pos[0] + util.noise(shakiness)),
            round(pos[1] + util.noise(shakiness)))
        canvas.paste(im['image'], pos)
        if 'bbox' in im:
            im['bbox'] = util.shift_rect(im['bbox'], pos)

    # group pairs to assign colors
    groups = []
    for pair in pairs:
        a, b = pair
        for grp in groups:
            if a in grp or b in grp:
                grp.add(a)
                grp.add(b)
        else:
            groups.append(set([a, b]))

    colors = {}
    for grp in groups:
        color = random.choice(COLORS)
        for id in grp:
            colors[id] = color

    # draw circles and arrows
    for id, im in images.items():
        annotate.circle(draw, im['bbox'], fill=colors[id])
        if random.random() < 0.3:
            annotate.arrow(draw, im['bbox'], fill=colors[id])

    # draw links
    for a, b in pairs:
        print('linking:', (a, b))
        annotate.link(
            draw, images[a]['bbox'][:2], images[b]['bbox'][:2], fill=colors[a])

    canvas.save(out)


if __name__ == '__main__':
    FACE_DIST_THRESH = 0.4

    faces, objects = [], []
    for path in images:
        faces.extend(load_images(path, 'faces'))
        objects.extend(load_images(path, 'objects'))

    print('faces:', len(faces))
    print('objects:', len(objects))
    fpairs, faces = get_similar(faces, FACE_DIST_THRESH, compare_faces, prefix='f')
    print('faces:', len(faces))
    opairs, objects = get_similar(objects, 2, compare.compute_dists, prefix='o')
    print('objects:', len(objects))

    pairs = fpairs + opairs
    images = {**faces, **objects}

    if pairs:
        print(pairs)
        images = prepare_images(images)
        render(images, pairs, out='output.jpg')