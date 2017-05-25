import re
import config
from . import entity
from itertools import permutations


def extract_patterns(a):
    ents = entity.get_entities(a)
    pairs = list(permutations(ents, 2))

    results = []
    for p in config.PATTERNS:
        for e, e_ in pairs:
            pat = p.format(re.escape(e), re.escape(e_))
            r = re.compile(pat)
            m = r.findall(a['text'])
            if m:
                results.extend(m)
    return results