import imagehash
import numpy as np
from PIL import Image
from itertools import combinations

hashfunc = imagehash.whash


def compute_dists(paths):
    # precompute distance matrix
    mat = np.zeros((len(paths), len(paths)))
    hashes = [hashfunc(Image.open(p)) for p in paths]
    for i, j in combinations(range(len(hashes)), 2):
        dist = hashes[i] - hashes[j]
        mat[i, j] = mat[j,i] = dist
    return mat


def compute_dist(img_a, img_b):
    hash_a = hashfunc(img_a)
    hash_b = hashfunc(img_b)
    return hash_a - hash_b
