import imagehash
import numpy as np
from PIL import Image
from itertools import combinations

hashfunc = imagehash.whash


def compute_dists(paths):
    """compute perceptual hash distance matrix for list of images"""
    mat = np.zeros((len(paths), len(paths)))
    hashes = [hashfunc(Image.open(p)) for p in paths]
    for i, j in combinations(range(len(hashes)), 2):
        dist = hashes[i] - hashes[j]
        mat[i, j] = mat[j,i] = dist
    return mat


def compute_dist(path_a, path_b):
    """compute perceptual hash distance between two images"""
    hash_a = hashfunc(Image.open(path_a))
    hash_b = hashfunc(Image.open(path_b))
    return hash_a - hash_b
