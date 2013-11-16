from requests.exceptions import RequestException as RemoteError
from cssselect import SelectorError
from requests.packages.urllib3.exceptions import LocationParseError as URLParseError

class NullSelectorError(Exception):
    def __init__(self, title, content):
        if not title and not content:
            self.msg = 'Item is missing title and content'
        elif not title:
            self.msg = 'Title is missing for item with content'
        elif not content:
            self.msg = 'Content is missing for item with title'
        self.title_or_content = title or content or ''
