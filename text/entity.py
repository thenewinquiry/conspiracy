# TODO this isn't really module-ready
import json
from glob import glob
from tqdm import tqdm
from collections import defaultdict

ENTS = ['ORG', 'GPE', 'NORP', 'PERSON', 'EVENT' , 'WORK_OF_ART']

index = defaultdict(list)
freq = defaultdict(int)
for f in tqdm(glob('../reality/data/**/*.json')):
    articles = json.load(open(f, 'r'))
    for a in articles:
        ents = [e.strip() for e, typ in a['entities'] if typ in ENTS and len(e) > 1]
        for e in ents:
            freq[e] += 1
            index[e].append(a['url'])

def most_common(d, n=10):
    ranked = sorted(d.items(), key=lambda x: x[1], reverse=True)
    return ranked[:n]

def least_common(d, n=10):
    ranked = sorted(d.items(), key=lambda x: x[1], reverse=True)
    return ranked[-n:]

print(most_common(freq))
print(least_common(freq))