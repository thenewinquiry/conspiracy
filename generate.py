import os
import json
import util
import config
import random
import logging
import numpy as np
from glob import glob
from itertools import chain
from datetime import datetime
from faces import compare_faces
from models import Img, Screenshot
from text import extract_screenshots
from PIL import Image, ImageDraw, ImageOps, ImageFont
from images import transform, layout, compare, annotate, mangle

# tensorflow logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

logger = logging.getLogger('conspiracy')


def get_similar(entities, thresh, comparator):
    """get pairs of similar images,
    according to the comparator (distance) function"""
    entities = [(k, v['path']) for k, v in entities.items()]
    ids, paths = zip(*entities)
    dists = comparator(paths)
    pairs = np.argwhere(dists <= thresh)

    # remove permutations
    pairs = set(tuple(sorted(p)) for p in pairs)

    # get entity ids and
    # filter out self-pairings
    pairs = [(ids[a], ids[b]) for a, b in pairs if a != b]

    # filter out pairs that are between two of the same images
    pairs = [(a, b) for a, b in pairs
             if a.split('_')[0] != b.split('_')[0]]

    # unique ids included in pairs
    ids = set(chain(*pairs))
    return pairs, ids



def render(images, pairs, out='output.jpg', shakiness=30, debug=True):
    """collages the images, annotating similar pairs by drawing links"""
    canvas = Image.new('RGB', config.SIZE, color=0)
    draw = ImageDraw.Draw(canvas)
    meta = {
        'name': out,
        'padding': config.PADDING,
        'images': {}
    }

    image_ref = {im.id: im for im in images}

    edges = []
    for a, b in pairs:
        a_im_path = a.rsplit('_', 2)[0]
        b_im_path = b.rsplit('_', 2)[0]
        edges.append((image_ref[a_im_path], image_ref[b_im_path]))
    images = util.walk_sort(edges)
    logger.info('after sorting: {}'.format(len(images)))

    if len(images) < config.MIN_IMAGES:
        return

    # get articles
    articles = [im.article for im in images if im.article is not None]
    articles = random.sample(articles, min(len(articles), 5))

    # extract screenshots of text
    texts = extract_screenshots(articles)
    vals = images + texts
    ims = [im.im for im in vals]
    logger.info('total source material: {}'.format(len(ims)))

    # layout images (may not include all)
    to_place = layout.layout(vals, canvas, shakiness=shakiness)

    # include at least one screenshot if there are any
    logger.info('extracted texts: {}'.format(texts))
    if not any(isinstance(im, Screenshot) for im, _ in to_place) and texts:
        logger.info('adding text')
        img, pos = to_place.pop(-1)
        txt = texts[0]
        txt.resize_to_limit(img.size)
        to_place.append((txt, pos))

    # paste selections into image
    placed_ents = []
    for img, pos in to_place:
        meta['images'][img.id] = {
            'pos': pos,
            'size': img.size
        }
        placed_ents.extend(list(img.entities.keys()))

        im = img.im
        if not isinstance(img, Screenshot) and random.random() <= config.MANGLE_PROB:
            im = mangle.mangle(img.im)
        canvas.paste(im, pos)
        if debug:
            label = getattr(img, 'path', img.id)
            annotate.label(draw, label, pos)
        for e in getattr(img, 'entities', {}).values():
            e['bbox'] = transform.shift_rect(e['bbox'], pos)

    # generate notes
    phrs = random.sample(config.NOTES, random.randint(2, 5))
    font = ImageFont.truetype('assets/font.ttf', 26)
    for ph in phrs:
        w, h = draw.textsize(ph, font=font)
        pos = (random.randint(20, config.SIZE[0]-w), random.randint(20, config.SIZE[1]-h))
        annotate.label(draw, ph, pos, bg=False, color=(255,255,255), font=font)

    # filter out pairs that have an unplaced image
    pairs = [(a, b) for a, b in pairs
             if a in placed_ents and b in placed_ents]

    eids = set(chain(*pairs))
    entities = {}
    for img in images:
        for id, e in img.entities.items():
            if id in eids:
                entities[id] = e

    canvas = ImageOps.expand(canvas, config.PADDING, fill=0)
    draw = ImageDraw.Draw(canvas)

    # draw circles and arrows
    colors = util.assign_entity_colors(pairs)
    for id, e in entities.items():
        bbox = [v+config.PADDING for v in e['bbox']]
        annotate.circle(draw, bbox, fill=colors[id])
        if random.random() < 0.3:
            annotate.arrow(draw, bbox, fill=colors[id])
        if debug:
            annotate.label(draw, id, bbox[:2])

    if len(pairs) < config.MIN_PAIRS:
        return

    # draw links
    for a, b in pairs:
        logger.info('linking: {}'.format((a, b)))
        ax, ay = entities[a]['bbox'][:2]
        bx, by = entities[b]['bbox'][:2]
        annotate.link(
            draw, (ax+config.PADDING, ay+config.PADDING), (bx+config.PADDING, by+config.PADDING), fill=colors[a])

    canvas.save(out)
    meta['size'] = canvas.size
    return meta


if __name__ == '__main__':
    from time import sleep
    logging.basicConfig(level=logging.INFO)

    # need to remove guardian images
    # they all have a huge watermark...
    g = glob('{}/data/theguardian.com/*.json'.format(config.REALITY_PATH))
    g_ids = []
    for p in g:
        for a in json.load(open(p, 'r')):
            g_ids.append('{}/data/_images/{}'.format(config.REALITY_PATH, util.hash(a['image'])))

    while True:
        misc_images = glob('assets/commons/*')
        news_images = [p for p in glob('{}/data/_images/*'.format(config.REALITY_PATH)) if p not in g_ids]
        logger.info('news images: {}, misc images: {}'.format(len(news_images), len(misc_images)))

        paths = random.sample(news_images, config.SAMPLE[0]) + random.sample(misc_images, config.SAMPLE[1])
        images = []
        for path in paths:
            try:
                images.append(Img(path))
            except OSError:
                continue
        logger.info('images: {}'.format(len(images)))

        logger.info('filtering similar images...')
        images = compare.filter_similar(images, config.IMAGE_SIM_THRESH)
        logger.info('remaining images: {}'.format(len(images)))

        faces, objects = {}, {}
        for img in images:
            faces.update(img.faces)
            objects.update(img.objects)

        logger.info('faces: {}'.format(len(faces)))
        logger.info('objects: {}'.format(len(objects)))
        fpairs, fids = get_similar(faces, config.FACE_DIST_THRESH, compare_faces)
        opairs, oids = get_similar(objects, config.OBJ_DIST_THRESH, compare.compute_dists)

        eids = fids.union(oids)
        pairs = fpairs + opairs

        # only include images which have entities present in pairs
        images = [img for img in images
                if any(id in eids for id in img.entities.keys())]
        logger.info('pairs: {}'.format(len(pairs)))
        logger.info('images: {}'.format(len(images)))

        if len(pairs) >= config.MIN_PAIRS:
            fname  = datetime.utcnow().strftime('%Y%m%d%H%M')
            meta = render(images, pairs, out='public/vault/{}.jpg'.format(fname))
            if meta is not None:
                with open('public/vault/{}.json'.format(fname), 'w') as f:
                    json.dump(meta, f)

                tmpl = open('assets/templates/index.html', 'r').read()
                figs = ['<figure><img src="{}"></figure>'.format(im.replace('public/', ''))
                        for im in sorted(glob('public/vault/*.jpg'), reverse=True)]
                html = tmpl.format(figures='\n'.join(figs))
                with open('public/index.html', 'w') as f:
                    f.write(html)
                util.sync()
        sleep(config.INTERVAL)