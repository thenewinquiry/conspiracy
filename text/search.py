import random
import requests
import lxml.html
import lxml.cssselect


def search(terms):
    """search for the specified terms,
    returning the text snippet of a random result"""
    params = {'q': ' '.join(['"{}"'.format(t) for t in terms]), 'start': 90}
    resp = requests.get('https://www.google.com/search', params=params)
    html = lxml.html.fromstring(resp.content)
    results = html.cssselect('.st')
    texts = [el.text_content() for el in results]
    return random.choice(texts)