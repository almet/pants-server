from collections import defaultdict

from pants.storage import DoesNotExist


class MemoryStorage(object):

    def __init__(self, *args, **kwargs):
        self.urls = defaultdict(list)
        self.call_info = defaultdict(list)

    def add_simplepush_url(self, userid, url):
        self.urls[userid].append(url)

    def get_simplepush_urls(self, userid):
        url = self.urls[userid]
        if not url:
            raise DoesNotExist(userid)
        return url

    def add_call_info(self, userid, token, session):
        self.call_info[userid].append((token, session))

    def get_call_info(self, userid):
        info = self.call_info[userid]
        if not info:
            raise DoesNotExist(userid)
        return info
