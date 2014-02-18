import functools

import hawkauthlib

from pyramid.request import Request
from pyramid.interfaces import IAuthenticationPolicy

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
