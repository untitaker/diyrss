from requests.exceptions import RequestException as RemoteError
from cssselect import SelectorError
from requests.packages.urllib3.exceptions import LocationParseError as URLParseError
from lxml.etree import LxmlError


class BrokenItemError(Exception):
    def __init__(self, item, title, content):
        self.item = item
        if not title and not content:
            self.msg = 'Item without content and title'
        elif not title:
            self.msg = 'Item without title'
        elif not content:
            self.msg = 'Item without content'
