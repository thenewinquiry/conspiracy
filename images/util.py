import random


def noise(strength=1):
    return (random.random() - 0.5) * strength


def scale_rect(rect, scale):
    return (rect[0] * scale[0], rect[1] * scale[1],
            rect[2] * scale[0], rect[3] * scale[1])


def shift_rect(rect, shift):
    return (rect[0] + shift[0], rect[1] + shift[1],
            rect[2] + shift[0], rect[3] + shift[1])


def resize_to_limit(img, target_size):
    x_t, y_t = target_size
    x_i, y_i = img.size
    if x_i <= x_t and y_i <= y_t:
        return img.copy()
    else:
        return resize_to_fit(img, target_size)


def resize_to_fit(img, target_size):
    x_t, y_t = target_size
    x_i, y_i = img.size
    x_scale = x_t/x_i
    y_scale = y_t/y_i
    scale = min(x_scale, y_scale)
    scaled_size = (
        int(x_i*scale),
        int(y_i*scale)
    )
    return img.resize(scaled_size)


def resize_to_fill(img, target_size):
    x_t, y_t = target_size
    x_i, y_i = img.size
    x_scale = x_t/x_i
    y_scale = y_t/y_i
    scale = max(x_scale, y_scale)

    x_new = int(x_i*scale)
    y_new = int(y_i*scale)
    img = img.resize((x_new, y_new))
    x_center = x_new/2
    y_center = y_new/2

    l = int(x_center - x_t/2)
    r = int(x_center + x_t/2)
    u = int(y_center - y_t/2)
    d = int(y_center + y_t/2)

    img = img.crop((l, u, r, d))

    # sometimes we may be one pixel off,
    # so just adjust if necessary
    if img.size != target_size:
        img = img.resize(target_size)
    return img
