import random
import numpy as np
from math import cos, sin, pi
from PIL import Image, ImageDraw


def ellipse_pt(th, x_c, y_c, a, b, rot):
    x = x_c + (a * cos(th) * cos(rot) - b * sin(th) * sin(rot))
    y = y_c + (a * cos(th) * sin(rot) - b * sin(th) * cos(rot))
    return x, y


def circle(draw, bbox, thickness=4, loops=2):
    offset = 0
    x1, y1, x2, y2 = bbox
    w, h = x2 - x1, y2 - y1
    x_c, y_c = x1 + w/2, y1 + h/2
    rot = (random.random() - 0.5) * 0.6
    a, b = w, h
    for loop in range(loops):
        for r in np.arange(0, 2*pi, 1/(max(w, h))):
            offset += random.random() - 0.5
            for i in range(thickness):
                x, y = ellipse_pt(r, x_c, y_c, a+i+offset, b+i+offset, rot)
                draw.point((x,y), fill=(255,0,0))
        a, b = a + 1, b + 1


def link(draw, frm, to, thickness=4):
    offset = 0
    x_1, y_1 = frm
    x_2, y_2 = to
    m = (y_2-y_1)/(x_2-x_1)
    b = y_1-(m*x_1)
    shakiness = 0.4
    for x in np.arange(x_1, x_2, 0.1):
        offset += (random.random() - 0.5) * shakiness
        for i in range(thickness):
            y = m * x + b
            if m < 0.1:
                y += i
                x_ = x
            else:
                x_ = x + i + offset
            draw.point((x_,y), fill=(255,0,0))


if __name__ == '__main__':
    im = Image.open('example.jpg')
    draw = ImageDraw.Draw(im)

    circle(draw, (100, 100, 200, 200))
    link(draw, (10, 10), (80, 80))

    im.save('output.jpg')
