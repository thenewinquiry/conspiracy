import imagehash
import numpy as np
from PIL import Image
from itertools import combinations


def compute_hashes(files, hashfunc=imagehash.whash):
    hashes, fnames = [], []
    for i, fname in enumerate(files):
        img = Image.open(fname)
        hash = hashfunc(img)
        hashes.append(hash)
        fnames.append(fname)
    return hashes, fnames


def compute_dists(hashes):
    # precompute distance matrix
    mat = np.zeros((len(hashes), len(hashes)))
    for i, j in combinations(range(len(hashes)), 2):
        dist = hashes[i] - hashes[j]
        mat[i, j] = mat[j,i] = dist
    return mat
