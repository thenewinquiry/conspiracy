import random
from PIL import Image, ImageFilter, ImageEnhance


def mangle(im):
    size = im.size
    scaled = random.randint(320, 1000)
    im.thumbnail((scaled, scaled))
    im = im.resize(size)
    im = im.filter(ImageFilter.UnsharpMask())
    contrast = ImageEnhance.Contrast(im)
    im = contrast.enhance(random.random() + 0.5)
    im.save('/tmp/output.jpg', quality=random.randint(10, 80))
    return Image.open('/tmp/output.jpg')
