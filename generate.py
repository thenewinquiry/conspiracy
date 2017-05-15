import json
import random
import annotate
import immanip
import numpy as np
from glob import glob
from PIL import Image, ImageDraw
from face_sim import compare
from itertools import chain
from pack import pack

SAMPLE = 200
SIZE = (1400, 800)
SHAKINESS = 30
MAX_SIZE = (0.5, 0.5)
MAX_SIZE = (MAX_SIZE[0]*SIZE[0], MAX_SIZE[1]*SIZE[1])
images = random.sample(glob('../reality/data/_images/*'), SAMPLE)


def get_objects(impath):
    imhash = impath.split('/')[-1]
    dir = 'data/objects/{}'.format(imhash)
    try:
        bboxes = json.load(open('{}/bboxes.json'.format(dir), 'r'))
        labels = json.load(open('{}/labels.json'.format(dir), 'r'))
        crops = glob('{}/*.jpg'.format(dir))
        return crops, bboxes, labels
    except FileNotFoundError:
        return [], [], []


def get_faces(impath):
    imhash = impath.split('/')[-1]
    dir = 'data/faces/{}'.format(imhash)
    try:
        bboxes = json.load(open('{}/bboxes.json'.format(dir), 'r'))
        crops = glob('{}/*.jpg'.format(dir))
        return crops, bboxes
    except FileNotFoundError:
        return [], []


def get_imhash(path):
    parts = path.split('/')
    imhash = parts[-2]
    id = parts[-1].split('.')[0]
    return imhash, id


def get_impath(imhash):
    return '../reality/data/_images/{}'.format(imhash)


all_faces = []
all_fbboxes = []
FACE_DIST_THRESH = 0.4
for impath in images:
    fpaths, fbboxes = get_faces(impath)
    opaths, obboxes, olabels = get_objects(impath)
    all_faces.extend(fpaths)
    all_fbboxes.extend(fbboxes)

print('faces:', len(all_faces))

dists = compare(all_faces)
idx = np.argwhere(dists <= FACE_DIST_THRESH)

# filter out self-pairings
idx = [(a, b) for a, b in idx if a != b]

# remove permutations
idx = set(tuple(sorted(l)) for l in idx)

# get unique dist mat indices
imdx = set(chain(*idx))

# create lookup for dist mat indices
# to image name hash
hash_idx = {}
for i in imdx:
    path = all_faces[i]
    imhash, id = get_imhash(path)
    hash_idx[i] = imhash

# filter out pairs that are between two of the same images
idx = [(a, b) for a, b in idx if hash_idx[a] != hash_idx[b]]

canvas = Image.new('RGB', SIZE, color=0)
draw = ImageDraw.Draw(canvas)
if idx:
    pair = random.choice(idx)
    imhashes = [(hash_idx[matidx], matidx) for matidx in pair]
    preppedims = []
    preppedbboxes = []
    matidxs = []
    # prepare images
    bbox_lookup = {}
    for imhash, matidx in imhashes:
        im = Image.open(get_impath(imhash))
        xo, yo = im.size
        im = immanip.resize_to_limit(im, MAX_SIZE)
        xn, yn = im.size
        resize_ratio = (xn/xo, yn/yo)

        # scale bbox accordingly
        bbox = all_fbboxes[matidx]
        bbox = (
            (bbox[0] * resize_ratio[0]), (bbox[1] * resize_ratio[1]),
            (bbox[2] * resize_ratio[0]), (bbox[3] * resize_ratio[1]))

        preppedims.append(im)
        preppedbboxes.append(bbox)
        matidxs.append(matidx)

    # this doesn't guarantee that every image will be included!
    packed = pack(preppedims, canvas)
    for im, pos, bbox, matidx in zip(preppedims, packed, preppedbboxes, matidxs):
        pos = (
            round(pos[0] + (random.random() - 0.5) * SHAKINESS),
            round(pos[1] + (random.random() - 0.5) * SHAKINESS))
        canvas.paste(im, pos)
        bbox = (
            bbox[0] + pos[0], bbox[1] + pos[1],
            bbox[2] + pos[0], bbox[3] + pos[1])
        bbox_lookup[matidx] = bbox
        annotate.circle(draw, bbox)

    # draw links
    for a, b in idx:
        try:
            bbox_a, bbox_b = bbox_lookup[a], bbox_lookup[b]
            annotate.link(
                draw,
                (bbox_a[0], bbox_a[1]),
                (bbox_b[0], bbox_b[1]))
        except KeyError:
            pass


    canvas.save('output.jpg')
else:
    print('nothing!')



# im = Image.open(impath)

# for bbox, (label, confidence) in zip(obj_bboxes, obj_labels):
#     if confidence > 0.3:
#         annotate.circle(draw, bbox)

# for bbox in face_bboxes:
#     annotate.circle(draw, bbox)

# im.save('output.jpg')