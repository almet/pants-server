from colander import (MappingSchema, SchemaNode, String, url)
from pyramid.security import Allow, Authenticated, authenticated_userid

from cornice import Service
from tokenlib.errors import Error as TokenError

from pants.storage import DoesNotExist


call_url = Service(name='call-url', path='/call-url')
call = Service(name='call', path='/calls/{token}')
calls = Service(name='calls', path='/calls')


def acl(request):
    return [(Allow, Authenticated, 'create-callurl'),
            (Allow, Authenticated, 'list-calls')]


def is_token_valid(request):
    token = request.matchdict['token']
    try:
        token = request.token_manager.parse_token(token.encode())
        request.validated['token'] = token
    except TokenError as e:
        request.errors.add('querystring', 'token', e.message)


class CallUrlSchema(MappingSchema):
    simple_push_url = SchemaNode(name='simple-push-url', validator=url,
                                 typ=String(), location="body")


@call_url.post(schema=CallUrlSchema, permission='create-callurl', acl=acl)
def create_call_link(request):
    """
    Generate a callurl based on user ID.
    """
    userid = authenticated_userid(request)

    # We need to try/except here in case the db fails.
    request.storage.add_simplepush_url(
        userid, request.validated['simple-push-url'])

    token = request.token_manager.make_token({"userid": userid})
    call_url = '{root}/call/{token}'.format(root=request.application_url,
                                            token=token)
    return {'call-url': call_url}


@call.get(validators=[is_token_valid], renderer='templates/call.jinja2')
def display_app(request):
    return request.validated['token']


@calls.get(permission='list-calls', acl=acl)
def list_calls(request):
    userid = authenticated_userid(request)
    try:
        call_info = request.storage.get_call_info(userid)
    except DoesNotExist:
        call_info = []

    return {'calls': [{'token': token, 'session': session}
                      for token, session in call_info]}
