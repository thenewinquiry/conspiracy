import random
import requests
import textwrap
import lxml.html
import lxml.cssselect
from glob import glob
from annotate import link
from PIL import Image, ImageDraw, ImageFont

fonts = glob('assets/fonts/*.ttf')


def noise(strength):
    return (random.random() - 0.5) * strength


def search(terms):
    params = {'q': ' '.join(['"{}"'.format(t) for t in terms]), 'start': 90}
    resp = requests.get('https://www.google.com/search', params=params)
    html = lxml.html.fromstring(resp.content)
    results = html.cssselect('.st')
    texts = [el.text_content() for el in results]
    return random.choice(texts)


def render_text(text, terms, size=(400, 200)):
    img = Image.new('RGB', size, (255,255,255))
    fnt = ImageFont.truetype(random.choice(fonts), 14)
    d = ImageDraw.Draw(img)
    shakiness = 8
    margin = offset = 20
    for line in textwrap.wrap(text, width=60):
        d.text((margin,offset), line, font=fnt, fill=(20,20,20))
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


if __name__ == '__main__':
    query = ['palantir', 'peter thiel']
    text = search(query)
    img = render_text(text, query)
    img.save('output.jpg')