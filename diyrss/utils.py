from flask.ext.cache import Cache
from StringIO import StringIO
import requests
from datetime import datetime
from werkzeug.contrib.atom import AtomFeed
from cssselect import GenericTranslator
import diyrss.errors as errors
import lxml.html
import lxml.etree

cache = Cache()

max_feed_size = 50 * 1024


@cache.memoize(timeout=60*5)
def _fetch_site(url):
    r = requests.get(url)
    return r.iter_content(max_feed_size).next()

def fetch_site(url):
    tree = lxml.html.fromstring(_fetch_site(url))
    return tree

def extract_from_tree(tree, selector):
    expression = GenericTranslator().css_to_xpath(selector)
    return tree.xpath(expression)

def to_string(node, strip=False):
    if type(node) is list:
        if node:
            node = node[0]
        else:
            return ''
    if strip:
        return lxml.etree.tostring(node, method='text', encoding=unicode)
    else:
        return lxml.etree.tostring(node, encoding=unicode)

@cache.memoize(timeout=60)
def get_feed(url, main_selector, title_selector, content_selector, skip_broken=False):
    site = fetch_site(url)

    title = to_string(extract_from_tree(site, 'title'), strip=True)
    feed = AtomFeed(title, url=url, subtitle=title, author='Unknown')

    site.make_links_absolute(url)
    for i, article in enumerate(extract_from_tree(site, main_selector)):
        title = to_string(extract_from_tree(article, title_selector), strip=True)
        content = to_string(extract_from_tree(article, content_selector))
        try:
            if not title or not content:
                raise errors.NullSelectorError(title or None, content or None)
        except errors.NullSelectorError:
            if not skip_broken:
                raise
            continue

        feed.add(
            title,
            content,
            content_type='html',
            url=url,
            id=url + str(i),
            updated=datetime.strptime('20121217', '%Y%m%d'),
            published=datetime.strptime('20121217', '%Y%m%d')
        )

    return feed.get_response()
