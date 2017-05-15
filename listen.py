import json
import hashlib
import fasteners
from time import sleep
from faces import extract_faces
from objects import extract_objects

def hash(text):
    return hashlib.md5(text.encode('utf8')).hexdigest()


def on_article(article):
    print(article['url'])
    im = hash(article['image'])
    path = '../reality/data/_images/{}'.format(im)
    faces = extract_faces(path)
    objects = extract_objects(path)
    print('  detected {} faces, {} objects'.format(
        len(faces), len(objects)))


if __name__ == '__main__':
    while True:
        fifo = 'fifo'
        try:
            with fasteners.InterProcessLock('/tmp/{}.lock'.format(hash(fifo))):
                try:
                    with open(fifo, 'r+') as f:
                        for l in f:
                            article = json.loads(l.strip())
                            on_article(article)
                    open(fifo, 'w').close()
                except FileNotFoundError:
                    print('no fifo')
                sleep(10)
        except (KeyboardInterrupt, SystemExit):
            break