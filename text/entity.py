import json
from glob import glob
from tqdm import tqdm
from collections import defaultdict

ENTS = ['ORG', 'GPE', 'NORP', 'PERSON', 'EVENT' , 'WORK_OF_ART']


def get_entities(a):
    return set([e.strip() for e, typ in a['entities'] if typ in ENTS and len(e.strip()) > 1])


def most_common(d, n=10):
    ranked = sorted(d.items(), key=lambda x: x[1], reverse=True)
    return ranked[:n]


def least_common(d, n=10):
    ranked = sorted(d.items(), key=lambda x: x[1], reverse=True)
    return ranked[-n:]


if __name__ == '__main__':
    index = defaultdict(list)
    freq = defaultdict(int)
    for f in tqdm(glob('../reality/data/**/*.json')):
        articles = json.load(open(f, 'r'))
        for a in articles:
            ents = [e.strip() for e, typ in a['entities'] if typ in ENTS and len(e) > 1]
            for e in ents:
                freq[e] += 1
                index[e].append(a['url'])
    print(most_common(freq))
    print(least_common(freq))