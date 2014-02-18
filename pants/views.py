from cornice import Service
from tokenlib.errors import Error as TokenError


callurl = Service(name='callurl', path='/call-url')
call = Service(name='call', path='/call/{token}')

def is_authenticated(request):
    """Validates that an user is authenticated and extracts its userid"""
    request.validated['userid'] = 'n1k0';


def is_token_valid(request):
    token = request.matchdict['token']
    try:
        token = request.token_manager.parse_token(token.encode())
        request.validated['token'] = token
    except TokenError as e:
        request.errors.add('querystring', 'token', e.message)


@callurl.post(permission='create')
def generate_callurl(request):
    """
    Generate a callurl based on user ID.
    """
    token = request.token_manager.make_token({
        "userid": request.validated['userid'],
    })
    call_url = '{root}/call/{token}'.format(root=request.application_url,
                                            token=token)
    return {'call-url': call_url}


@call.get(validators=[is_token_valid], renderer='templates/call.jinja2')
def display_app(request):
    return request.validated['token']
