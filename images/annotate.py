import random
import numpy as np
from math import cos, sin, pi, atan2
from .util import noise


def ellipse_pt(th, x_c, y_c, a, b, rot):
    """compute x, y for an ellipsis with the specified params"""
    x = x_c + (a * cos(th) * cos(rot) - b * sin(th) * sin(rot))
    y = y_c + (a * cos(th) * sin(rot) - b * sin(th) * cos(rot))
    return x, y


def circle(draw, bbox, thickness=4, loops=2, fill=(255,0,0)):
    """draw a 'handdrawn' ellipse around a bounding box"""
    offset = 0
    x1, y1, x2, y2 = bbox
    w, h = x2 - x1, y2 - y1
    x_c, y_c = x1 + w/2, y1 + h/2
    rot = noise(0.6)
    a, b = w, h
    for loop in range(loops):
        for r in np.arange(0, 2*pi + random.random(), 1/(max(w, h))):
            offset += noise()
            for i in range(thickness):
                x, y = ellipse_pt(r, x_c, y_c, a+i+offset, b+i+offset, rot)
                draw.point((x,y), fill=fill)
        a, b = a + 1, b + 1


def link(draw, frm, to, thickness=4, shakiness=0.4, fill=(255,0,0)):
    """draw a 'handdrawn' line connecting two points"""
    offset = 0
    x_1, y_1 = frm
    x_2, y_2 = to
    m = (y_2-y_1)/(x_2-x_1)
    b = y_1-(m*x_1)
    for x in np.arange(x_1, x_2, 0.1):
        offset += noise(shakiness)
        for i in range(thickness):
            y = m * x + b
            if m < 0.1:
                y += i
                x_ = x
            else:
                x_ = x + i + offset
            draw.point((x_,y), fill=fill)


def rand_bbox_point(bbox):
    """choose a random point on a bounding box"""
    x1, y1, x2, y2 = bbox
    side = random.choice(['t', 'b', 'r', 'l'])
    if side == 't':
        y = y1
        x = random.randint(x1, x2)
    elif side == 'b':
        y = y2
        x = random.randint(x1, x2)
    elif side == 'l':
        x = x1
        y = random.randint(y1, y2)
    elif side == 'r':
        x = x2
        y = random.randint(y1, y2)
    return x, y


def angle(pt_a, pt_b):
    """computes the angle between two points"""
    x1, y1 = pt_a
    x2, y2 = pt_b
    return atan2(y2-y1, x2-x1)


def point(pt, angle, dist):
    """computes the point at a given angle and distance
    from another point"""
    x, y = pt
    return dist * cos(angle) + x, dist * sin(angle) + y,


def arrow(draw, bbox, thickness=3, fill=(0,255,0), arrlen=50, arrang=0.5):
    x1, y1, x2, y2 = bbox
    xc, yc = x1 + (x2-x1)/2, y1 + (y2-y1)/2
    bbox_pt = rand_bbox_point(bbox)
    theta = angle((xc, yc), bbox_pt)
    head = point(bbox_pt, theta, 20)
    tail = point(bbox_pt, theta, 20+arrlen)
    draw.line([head, tail], fill=fill, width=thickness)
    for ang in [arrang+theta, -arrang+theta]:
        arrwing = point(head, ang, 20)
        arrwing = (arrwing[0] + noise(10), arrwing[1] + noise(10))
        draw.line([head, arrwing], fill=fill, width=thickness)
