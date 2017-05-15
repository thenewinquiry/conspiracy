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

