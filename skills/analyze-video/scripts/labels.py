"""Texts of the choice page that the scripts write, read from the template (../assets/choose-takes.html).

Every string the user reads on the page lives in the template, so translating the template translates the page. The
strings the scripts build (the favorite's reason, the warnings, the name of a take) are its <meta name="label-..."> tags:
score-takes.py and cuts.py write "reason" and "warning" into sentences.json with them, and choose-takes.py the labels
of each row. A tag's content can carry {take} and {reason} placeholders.
"""
import html, os, re, sys

TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../assets/choose-takes.html")
_labels = {}


def label(name, **values):
    """Text of <meta name="label-<name>">, with its placeholders filled in."""
    if not _labels:
        page = open(TEMPLATE, encoding="utf-8").read()
        _labels.update((k, html.unescape(v)) for k, v in re.findall(r'<meta name="label-([a-z0-9-]+)" content="([^"]*)">', page))
    if name not in _labels:
        sys.exit('%s has no <meta name="label-%s" content="...">' % (TEMPLATE, name))
    text = _labels[name]
    for k, v in values.items():
        text = text.replace("{" + k + "}", str(v))
    return text


def take_name(key):
    """Name shown for a take: the key "Take 4+5" of sentences.json with the template's word for "Take"."""
    return label("take") + key[len("Take"):]
