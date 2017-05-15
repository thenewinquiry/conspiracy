import os
import json
import dlib
import numpy as np
from PIL import Image

# HOG face detector
face_detector = dlib.get_frontal_face_detector()


def extract_faces(path):
    fname = path.split('/')[-1]
    dir = 'data/faces/{}'.format(fname)
    if os.path.exists(dir):
        return []
    else:
        os.makedirs(dir)
    bboxes = []
    image = Image.open(path).convert('RGB')
    detected = face_detector(np.array(image), 2)
    if detected:
        for i, rect in enumerate(detected):
            bbox = (rect.left(), rect.top(), rect.right(), rect.bottom())
            crop = image.crop(bbox)
            crop.save('{}/{}.jpg'.format(dir, i))
            bboxes.append(bbox)
        with open('{}/bboxes.json'.format(dir), 'w') as f:
            json.dump(bboxes, f)
    return detected


if __name__ == '__main__':
    from glob import glob
    from parallel import run_parallel
    run_parallel(glob('../reality/data/_images/*'), extract_faces)
