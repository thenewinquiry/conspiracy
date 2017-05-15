import os
import json
import numpy as np
from PIL import Image
from darkflow.net.build import TFNet

opts = {
    'model': 'assets/models/yolo/yolo.cfg',
    'load': 'assets/models/yolo/yolo.weights',
    'config': 'assets/models/yolo/',
    'threshold': 0.1
}
tfnet = TFNet(opts)


def extract_objects(path):
    fname = path.split('/')[-1]
    dir = 'data/objects/{}'.format(fname)
    if os.path.exists(dir):
        return []
    else:
        os.makedirs(dir)
    try:
        image = Image.open(path).convert('RGB')
    except OSError:
        return []
    detected = tfnet.return_predict(np.array(image))
    detected = [{
        'label': r['label'],
        'confidence': r['confidence'],
        'bbox': (
            r['topleft']['x'], r['topleft']['y'],
            r['bottomright']['x'], r['bottomright']['y'],
        )
    } for r in detected]
    bboxes = []
    labels = [(r['label'], float(r['confidence'])) for r in detected]
    for i, r in enumerate(detected):
        crop = image.crop(r['bbox'])
        crop.save('{}/{}.jpg'.format(dir, i))
        bboxes.append(r['bbox'])
    with open('{}/bboxes.json'.format(dir), 'w') as f:
        json.dump(bboxes, f)
    with open('{}/labels.json'.format(dir), 'w') as f:
        json.dump(labels, f)
    return detected



if __name__ == '__main__':
    from glob import glob
    from tqdm import tqdm
    for p in tqdm(glob('../reality/data/_images/*')):
        extract_objects(p)
