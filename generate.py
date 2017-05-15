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
from similarity import compute_dist, compute_dists

SAMPLE = 200
SIZE = (1400, 800)
SHAKINESS = 30
MAX_SIZE = (0.5, 0.5)
MAX_SIZE = (MAX_SIZE[0]*SIZE[0], MAX_SIZE[1]*SIZE[1])
images = random.sample(glob('../reality/data/_images/*'), SAMPLE)

def noise(strength):
    return (random.random() - 0.5) * strength


def get_objects(impath):
    imid = impath.split('/')[-1]
    dir = 'data/objects/{}'.format(imid)
    try:
        bboxes = json.load(open('{}/bboxes.json'.format(dir), 'r'))
        labels = json.load(open('{}/labels.json'.format(dir), 'r'))
        crops = glob('{}/*.jpg'.format(dir))
        return [{
            'path': c,
            'bbox': b,
            'label': l,
            'imid': imid
        } for c, b, l in zip(crops, bboxes, labels)]
    except FileNotFoundError:
        return []


def get_faces(impath):
    imid = impath.split('/')[-1]
    dir = 'data/faces/{}'.format(imid)
    try:
        bboxes = json.load(open('{}/bboxes.json'.format(dir), 'r'))
        crops = glob('{}/*.jpg'.format(dir))
        return [{
            'path': c,
            'bbox': b,
            'imid': imid
        } for c, b in zip(crops, bboxes)]
    except FileNotFoundError:
        return []


def get_impath(imid):
    return '../reality/data/_images/{}'.format(imid)

def im_dist(imid_a, imid_b):
    ims = [Image.open(get_impath(im)) for im in [imid_a, imid_b]]
    return compute_dist(*ims)


def filter_pairs(pairs, images):
    # remove permutations
    pairs = set(tuple(sorted(p)) for p in pairs)

    # filter out self-pairings
    # filter out pairs that are between two of the same images
    # filter out pairs that are from really similar images
    pairs = [(a, b) for a, b in pairs
             if a != b
             and images[a]['imid'] != images[b]['imid']
             and im_dist(images[a]['imid'], images[b]['imid']) > 0.5] # TODO adjust this thresh
    return pairs


def get_similar_faces(faces, thresh):
    dists = compare([f['path'] for f in faces])
    pairs = np.argwhere(dists <= thresh)
    pairs = filter_pairs(pairs, faces)

    # get unique dist mat indices
    indices = set(chain(*pairs))
    return pairs, {idx: faces[idx] for idx in indices}


def get_similar_objects(objs, thresh):
    dists = compute_dists([o['path'] for o in objs])
    pairs = np.argwhere(dists <= thresh)
    pairs = filter_pairs(pairs, objs)

    # get unique dist mat indices
    indices = set(chain(*pairs))
    return pairs, {idx: objs[idx] for idx in indices}


def scale_rect(rect, scale):
    return (rect[0] * scale[0], rect[1] * scale[1],
            rect[2] * scale[0], rect[3] * scale[1])


def shift_rect(rect, shift):
    return (rect[0] + shift[0], rect[1] + shift[1],
            rect[2] + shift[0], rect[3] + shift[1])


def prepare_images(images):
    for image in images.values():
        im = Image.open(get_impath(image['imid']))
        xo, yo = im.size

        im = immanip.resize_to_limit(im, MAX_SIZE)
        xn, yn = im.size

        resize_ratio = (xn/xo, yn/yo)

        # scale bbox accordingly
        image['bbox'] = scale_rect(image['bbox'], resize_ratio)
        image['image'] = im
    return images


def render(images, pairs, out='output.jpg'):
    canvas = Image.new('RGB', SIZE, color=0)
    draw = ImageDraw.Draw(canvas)

    # layout images
    # this doesn't guarantee that every image will be included!
    packed = pack([im['image'] for im in images.values()], canvas)
    for im, pos in zip(images.values(), packed):
        pos = (
            round(pos[0] + noise(SHAKINESS)),
            round(pos[1] + noise(SHAKINESS)))
        canvas.paste(im['image'], pos)
        im['bbox'] = shift_rect(im['bbox'], pos)

    # draw circles
    for im in images.values():
        annotate.circle(draw, im['bbox'])

    # draw links
    for a, b in pairs:
        annotate.link(draw, images[a]['bbox'][:2], images[b]['bbox'][:2])
    canvas.save(out)

if __name__ == '__main__':
    FACE_DIST_THRESH = 0.4

    faces = []
    objects = []
    for path in images:
        faces.extend(get_faces(path))
        objects.extend(get_objects(path))

    print('faces:', len(faces))
    print('objects:', len(objects))
    fpairs, faces = get_similar_faces(faces, FACE_DIST_THRESH)
    opairs, objects = get_similar_objects(objects, FACE_DIST_THRESH)

    # since indices will collide, add prefixes
    fpairs = [('f{}'.format(a), 'f{}'.format(b)) for a, b in fpairs]
    faces = {'f{}'.format(k): v for k, v in faces.items()}
    opairs = [('o{}'.format(a), 'o{}'.format(b)) for a, b in opairs]
    objects = {'o{}'.format(k): v for k, v in objects.items()}
    pairs = fpairs + opairs

    if pairs:
        images = prepare_images(objects)
        render(images, opairs, out='output.jpg')
        # images = prepare_images({**faces, **objects})
        # render(images, fpairs + opairs, out='output.jpg')