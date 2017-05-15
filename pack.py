from rectpack import newPacker


def pack(images, canvas):
    packer = newPacker()
    rects = [im.size for im in images]
    for rect in rects:
        packer.add_rect(*rect)
    packer.add_bin(*canvas.size)
    packer.pack()
    packed = packer[0]
    # return [(r.x, r.y, r.x + r.width, r.y + r.height) for r in packed]
    return [(r.x, r.y) for r in packed]

