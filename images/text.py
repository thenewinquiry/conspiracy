import random
import textwrap
from glob import glob
from PIL import Image, ImageDraw, ImageFont
from .annotate import link
from .util import noise

fonts = glob('assets/fonts/*.ttf')


def render_text(text, terms, size=(400, 200), fill=(20,20,20)):
    """renders text to an image,
    underlining the specified terms"""
    img = Image.new('RGB', size, (255,255,255))
    fnt = ImageFont.truetype(random.choice(fonts), 14)
    d = ImageDraw.Draw(img)
    shakiness = 8
    margin = offset = 20
    for line in textwrap.wrap(text, width=60):
        d.text((margin,offset), line, font=fnt, fill=fill)
        offset += fnt.getsize(line)[1]
        for term in terms:
            if term in line.lower():
                # compute width of text before the term
                i = line.lower().index(term)
                before_width = fnt.getsize(line[:i])[0]

                # compute width of the term
                term_width = fnt.getsize(term)[0]

                # underline the term
                x1, y1 = margin + before_width + noise(shakiness), offset + noise(shakiness)
                x2, y2 = x1 + term_width + noise(shakiness), y1 + noise(shakiness)
                link(d, (x1, y1), (x2, y2))

    # trim to fit
    return img.crop((0,0,size[0],offset+margin))
