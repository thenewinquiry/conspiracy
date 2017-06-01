import config
import random
import hashlib
import subprocess
import networkx as nx


def hash(text):
    return hashlib.md5(text.encode('utf8')).hexdigest()


def noise(strength=1):
    return (random.random() - 0.5) * strength


def walk_sort(edges):
    """sort nodes by degree, starting from
    the highest-degree node, identifying connected nodes,
    selecting the highest-degree node from those, etc.
    only walks connected nodes so the returned
    nodes may be less than specified by the edges"""
    g = nx.Graph()
    g.add_edges_from(edges)
    connected = set()
    degree = nx.degree(g)
    ordering = []
    while degree:
        next = max_degree_node(g, degree, connected)
        if next is not None:
            ordering.append(next)
        else:
            break
    return ordering


def max_degree_node(g, d, connected):
    """select the highest-degree node from
    a set of connected nodes"""
    if not connected:
        deg = d
    else:
        deg = {k: v for k, v in d.items() if k in connected}
    if not deg:
        return None
    n = max(deg.keys(), key=lambda k: deg[k])
    d.pop(n)
    for n_ in g.neighbors(n):
        connected.add(n_)
    return n


def assign_entity_colors(pairs):
    """assign entities colors
    based on what pair groups they're part of"""
    groups = []
    for a, b in pairs:
        for grp in groups:
            if a in grp or b in grp:
                grp.add(a)
                grp.add(b)
        else:
            groups.append(set([a, b]))

    colors = {}
    for grp in groups:
        color = random.choice(config.COLORS)
        for id in grp:
            colors[id] = color
    return colors


def sync():
    proc = subprocess.Popen([
        'rsync',
        '-rv',
        '--delete',
        'public/',
        config.REMOTE
    ])
    proc.communicate()
