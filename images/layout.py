import util
import config
from rectpack import newPacker


def pack(images, canvas):
    """packs images into a canvas;
    does not guarantee that all images will fit"""
    packer = newPacker()
    rects = [im.size for im in images]
    for rect in rects:
        packer.add_rect(*rect)
    packer.add_bin(*canvas.size)
    packer.pack()
    packed = packer[0]
    return [(r.x, r.y) for r in packed]


def layout(images, canvas, shakiness=0):
    """compute image layout;
    this doesn't guarantee that every image will be included!
    this resizes overflowing images to fit.
    """
    to_place = []
    ims = [im.im for im in images]
    packed = pack(ims, canvas)
    for img, pos in zip(images, packed):
        pos = (
            round(pos[0] + util.noise(shakiness)),
            round(pos[1] + util.noise(shakiness)))

        if pos[0] + img.size[0] > config.SIZE[0] or pos[1] + img.size[1] > config.SIZE[1]:
            # compute overflow
            new_size = (config.SIZE[0] - pos[0], config.SIZE[1] - pos[1])
            img.resize_to_limit(new_size)

        to_place.append((img, pos))
    return to_place
