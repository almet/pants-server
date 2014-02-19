import functools
import os
import unittest2 as unittest

import hawkauthlib
import webtest

from pyramid.interfaces import IAuthenticationPolicy
from pyramid.request import Request

__HERE__ = os.path.dirname(os.path.abspath(__file__))


def sign_requests(user='alexis'):
    """Monkey patch the self.app object so that requests are signed with an
       Hawk token.
    """
    def wrapper(f):
        @functools.wraps(f)
        def wrapped(self, *args, **kwargs):
            auth_policy = self.app.app.registry.getUtility(
                IAuthenticationPolicy)
            req = Request.blank('http://localhost')
            auth_token, auth_secret = auth_policy.encode_hawk_id(req, user)

            # Monkey-patch the app to sign all requests with the token.
            def new_do_request(req, *args, **kwds):
                hawkauthlib.sign_request(req, auth_token, auth_secret)
                return orig_do_request(req, *args, **kwds)
            orig_do_request = self.app.do_request
            self.app.do_request = new_do_request
            return f(self, *args, **kwargs)
        return wrapped
    return wrapper


class BaseWebTest(unittest.TestCase):

    def setUp(self):
        self.app = webtest.TestApp("config:tests.ini", relative_to=__HERE__)
        self.token_manager = self.app.app.registry.token_manager
        self.storage = self.app.app.registry.storage
        self.simple_push_url = 'https://token.services.mozilla.org'
