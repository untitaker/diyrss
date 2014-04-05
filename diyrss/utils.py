from flask.ext.cache import Cache
import requests
from datetime import datetime
from werkzeug.contrib.atom import AtomFeed
from cssselect import GenericTranslator
import lxml.html
import lxml.etree
import diyrss.errors as errors

cache = Cache()

max_feed_size = 50 * 1024


@cache.memoize(timeout=60*5)
def _fetch_site(url):
    r = requests.get(url)
    try:
        return r.iter_content(max_feed_size).next()
    except StopIteration:
        raise errors.RemoteError()


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


def extract_link(headline):
    if isinstance(headline, list):
        if not headline:
            return None
        headline = headline[0]

    def inner():
        yield headline.attrib.get('href', '').strip()
        for a in extract_from_tree(headline, 'a'):
            yield a.attrib.get('href', '').strip()
        yield None

    return filter(bool, inner())


@cache.memoize(timeout=60)
def get_feed(url, main_selector, title_selector, content_selector):
    site = fetch_site(url)

    title = to_string(extract_from_tree(site, 'title'),
                      strip=True) or u'[unknown]'
    feed = AtomFeed(title, url=url, subtitle=title, author=u'[unknown]')

    site.make_links_absolute(url)
    for i, item in enumerate(extract_from_tree(site, main_selector)):
        title_element = extract_from_tree(item, title_selector)
        title = to_string(title_element, strip=True)
        content = to_string(extract_from_tree(item, content_selector))
        if not title or not content:
            raise errors.BrokenItemError(
                to_string(item, strip=False),
                title,
                content
            )
        feed.add(
            title,
            content,
            content_type='html',
            url=extract_link(title_element) or url,
            id=url + str(i),
            updated=datetime.strptime('20121217', '%Y%m%d'),
            published=datetime.strptime('20121217', '%Y%m%d')
        )

    return feed.get_response()
