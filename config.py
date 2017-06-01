PATTERNS = [
    '{} is [^.?!,]+ {}',
    '{} was [^.?!,]+ {}',
    '{} will [^.?!,]+ {}',
    '{} paid [^.?!,]+ {}',
    '{} agreed [^.?!,]+ {}',
    '{} claims [^.?!,]+ {}',
    '{} denied [^.?!,]+ {}',
]

NOTES = [
    '???',
    'look closely',
    'doesn\'t add up...',
    'huge if true',
    'coincidence??',
    'ok...',
    'remind you of anything??',
    'the SAME',
    'buy my nootropics stack',
    '->$ follow the money ->$',
    'come back to this',
    'SOROS',
    'where were they on that night?',
    'alex was right',
    'if you know what this is tell me!',
    'DELETE after reading',
    'wtf??',
    'hmm...',
    'they cant HIDE this',
    'just making connections',
    'LIES'
]


SIZE = (1400, 800)
MAX_SIZE = (0.3, 0.3)
COLORS = [(255,0,0), (0, 100, 255), (6, 214, 44), (242, 226, 4)]
MIN_PAIRS = 5
MIN_IMAGES = 5
MANGLE_PROB = 0.4
PADDING = 50
MAX_SIZE = (MAX_SIZE[0]*SIZE[0], MAX_SIZE[1]*SIZE[1])
INTERVAL = 60 * 60 * 5

SAMPLE = (250, 400)
FACE_DIST_THRESH = 0.3
OBJ_DIST_THRESH = 2
IMAGE_SIM_THRESH = 3
REALITY_PATH = '../reality'
REMOTE = 'ftseng@darkinquiry.com:/srv/conspiracy/'
