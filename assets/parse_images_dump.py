import os
import hashlib
import sqlparse
import fileinput
from glob import glob

SAVE_EVERY = 100000


if __name__ == '__main__':
    for d in ['commons', 'commons_urls']:
        if not os.path.isdir(d):
            os.makedirs(d)

    i = 0
    dump = []
    # the encoding doesn't seem correct for some lines, but this is what
    # the documentation says the encoding is
    for line in fileinput.input(openhook=fileinput.hook_encoded('iso8859-1')):
        if line.startswith('INSERT INTO'):
            for v in sqlparse.parse(line):
                for t in v.tokens:
                    if isinstance(t, sqlparse.sql.Parenthesis):
                        # first token is the image file name
                        # it's quoted in single quotes, so trim those
                        # unescape the string
                        fname = str(list(t.flatten())[1])[1:-1].encode('utf8').decode('unicode_escape')
                        hash = hashlib.md5(fname.encode('iso8859-1')).hexdigest()
                        url = 'https://upload.wikimedia.org/wikipedia/commons/{}/{}/{}'.format(
                            hash[0],
                            hash[:2],
                            fname)
                        dump.append(url)
                        i += 1
                        if i % SAVE_EVERY == 0:
                            print('saving... (processed {})'.format(i))
                            n = len(glob('commons_urls/*'))
                            with open('commons_urls/{}'.format(n), 'w') as f:
                                f.write('\n'.join(dump))
                            dump = []