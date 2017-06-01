import json
import config
from PIL import Image
from glob import glob
from util import hash
from images import transform, compare


class Img():
    def __init__(self, path):
        self.path = path
        self.id = path.split('/')[-1]
        self.faces = self._load_entities('faces')
        self.objects = self._load_entities('objects')
        self.im = Image.open(self.path).convert('RGBA')
        self.resize_to_limit(config.MAX_SIZE)
        self.hash = compare.hashfunc(self.im)

    def _load_entities(self, type):
        dir = 'data/{}/{}'.format(type, self.id)
        try:
            bboxes = json.load(open('{}/bboxes.json'.format(dir), 'r'))
            crops = glob('{}/*.jpg'.format(dir))
            return {
                '{}_{}_{}'.format(self.id, i, type[0]): {
                    'path': c,
                    'bbox': b
                } for i, (c, b) in enumerate(zip(crops, bboxes))
            }
        except FileNotFoundError:
            return {}

    @property
    def entities(self):
        return {**self.faces, **self.objects}

    @property
    def size(self):
        return self.im.size

    def resize_to_limit(self, size):
        xo, yo = self.im.size

        self.im = transform.resize_to_limit(self.im, size)
        xn, yn = self.im.size

        resize_ratio = (xn/xo, yn/yo)

        # scale bboxes accordingly
        for e in self.entities.values():
            e['bbox'] = transform.scale_rect(e['bbox'], resize_ratio)


    @property
    def article(self):
        # ugh no reverse lookup, brute force search for now
        files = glob('../reality/data/**/*.json')
        for path in files:
            data = json.load(open(path, 'r'))
            for a in data:
                if hash(a['image']) == self.id:
                    return a


class Screenshot():
    def __init__(self, im):
        self.id = '{}_s'.format(id(im))
        self.im = im
        self.entities = {}

    @property
    def size(self):
        return self.im.size

    def resize_to_limit(self, size):
        xo, yo = self.im.size
        self.im = transform.resize_to_limit(self.im, size)
