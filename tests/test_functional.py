import tokenlib

from support import sign_requests, BaseWebTest


class TokenCreationTest(BaseWebTest):

    # POST /call-url
    def test_token_creation_requires_authn(self):
        resp = self.app.post('/call-url', status=401)
        auth_header = resp.headers.get('WWW-Authenticate')
        self.assertEquals(auth_header, 'Hawk', auth_header)

    @sign_requests(user='n1k0')
    def test_token_creation_needs_simple_push_url(self):
        resp = self.app.post_json('/call-url', status=400)
        self.assertEquals(resp.json['status'], 'error')
        error = resp.json['errors'][0]
        self.assertEquals(error['name'], 'simple-push-url')
        self.assertEquals(error['description'], 'simple-push-url is missing')

    @sign_requests(user='n1k0')
    def test_token_creation_needs_simple_push_url_to_be_valid(self):
        resp = self.app.post_json('/call-url', {
            'simple-push-url': 'nohttp'
        }, status=400)
        self.assertEquals(resp.json['status'], 'error')
        error = resp.json['errors'][0]
        self.assertEquals(error['name'], 'simple-push-url')
        self.assertEquals(error['description'], 'Must be a URL')

    @sign_requests(user='n1k0')
    def test_token_creation_generates_a_valid_token(self):
        resp = self.app.post_json('/call-url', {
            'simple-push-url': self.simple_push_url
        }, status=200)

        token = resp.json['call-url'].split('/')[-1]
        parsed_token = self.token_manager.parse_token(token.encode())

        self.assertEquals(parsed_token['userid'], 'n1k0')

    @sign_requests(user='n1k0')
    def test_token_creation_returns_an_absolute_url(self):
        resp = self.app.post_json('/call-url', {
            'simple-push-url': self.simple_push_url
        }, status=200)

        self.assertIn('call-url', resp.json)
        call_url = resp.json['call-url']
        self.assertTrue(call_url.startswith('http://localhost/call/'),
                        call_url)

    @sign_requests(user='n1k0')
    def test_token_creation_stores_push_url(self):
        self.app.post_json('/call-url', {
            'simple-push-url': self.simple_push_url
        }, status=200)
        self.assertIn(self.simple_push_url,
                      self.storage.get_simplepush_urls('n1k0'))


class CallUrlTest(BaseWebTest):

    # GET /calls/<token>
    def test_invalid_callurl_token_returns_400(self):
        # Let's forge a token with an invalid secret.
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
    @sign_requests(user='n1k0')
    def test_listed_calls_exist(self):
        self.storage.add_call_info('n1k0', 'token', 'sessionId')
        resp = self.app.get('/calls', status=200)
        self.assertEquals(resp.json, {u'calls': [{
            u'session': u'sessionId',
            u'token': u'token'
        }]})
