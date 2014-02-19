import tokenlib

from support import authenticate, BaseWebTest


class TokenCreationTest(BaseWebTest):

    # POST /call-url
    def test_token_creation_requires_authn(self):
        resp = self.app.post('/call-url', status=401)
        auth_header = resp.headers.get('WWW-Authenticate')
        self.assertEquals(auth_header, 'Hawk', auth_header)

    @authenticate(user='n1k0')
    def test_token_creation_needs_simple_push_url(self):
        resp = self.app.post_json('/call-url', status=400)
        self.assertEquals(resp.json['status'], 'error')
        error = resp.json['errors'][0]
        self.assertEquals(error['name'], 'simple_push_url')
        self.assertEquals(error['description'], 'simple_push_url is missing')

    @authenticate(user='n1k0')
    def test_token_creation_needs_simple_push_url_to_be_valid(self):
        resp = self.app.post_json('/call-url', {
            'simple_push_url': 'nohttp'
        }, status=400)
        self.assertEquals(resp.json['status'], 'error')
        error = resp.json['errors'][0]
        self.assertEquals(error['name'], 'simple_push_url')
        self.assertEquals(error['description'], 'Must be a URL')

    @authenticate(user='n1k0')
    def test_token_creation_generates_a_valid_token(self):
        resp = self.app.post_json('/call-url', {
            'simple_push_url': self.simple_push_url
        }, status=200)

        # extract token from call url
        call_token = resp.json['call_url'].split('/')[-1]
        parsed_token = self.token_manager.parse_token(call_token.encode())

        self.assertEquals(parsed_token['userid'], 'n1k0')

    @authenticate(user='n1k0')
    def test_token_creation_returns_an_absolute_url(self):
        resp = self.app.post_json('/call-url', {
            'simple_push_url': self.simple_push_url
        }, status=200)

        self.assertIn('call_url', resp.json)
        call_url = resp.json['call_url']
        self.assertTrue(call_url.startswith('http://localhost/call/'),
                        call_url)

    @authenticate(user='n1k0')
    def test_token_creation_stores_push_url(self):
        self.app.post_json('/call-url', {
            'simple_push_url': self.simple_push_url
        }, status=200)
        self.assertIn(self.simple_push_url,
                      self.storage.get_simplepush_urls('n1k0'))


class CallUrlTest(BaseWebTest):

    # GET /calls/<call_token>
    def test_invalid_callurl_token_returns_400(self):
        # Let's forge a call token with an invalid secret.
        invalid_token = tokenlib.make_token({'userid': 'h4x0r'},
                                            secret='I AM MEAN')
        resp = self.app.get('/calls/%s' % invalid_token, status=400)
        self.assertEquals(resp.json['status'], 'error')
        self.assertEquals(resp.json['errors'][0]['description'],
                          'token has invalid signature')

    def test_valid_callurl_returns_an_html_page(self):
        valid_token = self.token_manager.make_token({'userid': 'n1k0'})
        resp = self.app.get('/calls/%s' % valid_token, status=200)
        self.assertEquals(resp.headers['Content-Type'],
                          'text/html; charset=UTF-8')


class ListIncomingCallsTest(BaseWebTest):

    # GET /calls
    @authenticate(user='n1k0')
    def test_listing_existing_calls_work(self):
        self.storage.add_call_info('n1k0', 'token', 'sessionId')
        resp = self.app.get('/calls', status=200)
        self.assertEquals(resp.json, {u'calls': [{
            u'session': u'sessionId',
            u'provider_token': u'token'
        }]})

    @authenticate(user='n1k0')
    def test_listing_unexisting_calls_returns_empty_list(self):
        resp = self.app.get('/calls', status=200)
        self.assertEquals(resp.json, {u'calls': []})
