import os
import unittest2 as unittest

import tokenlib
import webtest

__HERE__ = os.path.dirname(os.path.abspath(__file__))

class FunctionalTest(unittest.TestCase):

    def setUp(self):
        self.app = webtest.TestApp("config:tests.ini", relative_to=__HERE__)
        self.token_manager = self.app.app.registry.token_manager

    def test_token_creation_generates_a_valid_token(self):
        resp = self.app.post('/call-url', status=200)

        token = resp.json['call-url'].split('/')[-1]
        parsed_token = self.token_manager.parse_token(token.encode())

        self.assertEquals(parsed_token['userid'], 'n1k0')

    def test_token_creation_returns_an_absolute_url(self):
        resp = self.app.post('/call-url', status=200)
        self.assertIn('call-url', resp.json)
        call_url = resp.json['call-url']
        self.assertTrue(call_url.startswith('http://localhost/call/'), call_url)

    def test_token_creation_validates_authentication(self):
        pass

    def test_invalid_callurl_token_returns_400(self):
        # Let's forge a token with an invalid secret.
        invalid_token = tokenlib.make_token({'userid': 'h4x0r'},
                                            secret='I AM MEAN')
        resp = self.app.get('/call/%s' % invalid_token, status=400)
        self.assertEquals(resp.json['status'], 'error')
        self.assertEquals(resp.json['errors'][0]['description'],
                          'token has invalid signature')

    def test_valid_callurl_returns_an_html_page(self):
        valid_token = self.token_manager.make_token({'userid': 'n1k0'})
        resp = self.app.get('/call/%s' % valid_token, status=200)
        self.assertEquals(resp.headers['Content-Type'], 'text/html; charset=UTF-8')
