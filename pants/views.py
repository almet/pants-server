from colander import (MappingSchema, SchemaNode, String, url)
from pyramid.security import Allow, Authenticated, authenticated_userid

from cornice import Service
from tokenlib.errors import Error as TokenError


callurl = Service(name='callurl', path='/call-url')
call = Service(name='call', path='/call/{token}')


def acl(request):
    return [(Allow, Authenticated, 'create-callurl')]


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


@callurl.post(schema=CallUrlSchema, permission='create-callurl', acl=acl)
def generate_callurl(request):
    """
    Generate a callurl based on user ID.
    """
    userid = authenticated_userid(request)
    token = request.token_manager.make_token({"userid": userid})
    call_url = '{root}/call/{token}'.format(root=request.application_url,
                                            token=token)
    return {'call-url': call_url}


@call.get(validators=[is_token_valid], renderer='templates/call.jinja2')
def display_app(request):
    return request.validated['token']
