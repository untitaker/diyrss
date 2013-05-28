from flask.ext.cache import Cache
from flask.ext.assets import Environment as AssetsEnv, \
                             Bundle as AssetsBundle
from StringIO import StringIO
import requests
from datetime import datetime
from werkzeug.contrib.atom import AtomFeed
from cssselect import GenericTranslator
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
        return lxml.etree.tostring(node, method='text')
    else:
        return lxml.etree.tostring(node)

@cache.memoize(timeout=60)
def get_feed(url, main_selector, title_selector, content_selector):
    site = fetch_site(url)

    title = to_string(extract_from_tree(site, 'title'), strip=True)
    feed = AtomFeed(title, url=url, subtitle=title, author='Unknown')

    site.make_links_absolute(url)
    for i, article in enumerate(extract_from_tree(site, main_selector)):
        title = to_string(extract_from_tree(article, title_selector), strip=True)
        content = to_string(extract_from_tree(article, content_selector))
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


assets = AssetsEnv()
js = AssetsBundle('bootstrap/js/bootstrap.min.js', 'main.js',
                  filters='jsmin', output='gen/min.js')
assets.register('js_all', js)

css = AssetsBundle('main.less', filters='less', output='gen/min.css')
assets.register('css_all', css)
