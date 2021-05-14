import json
from flask import request, abort, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

AUTH0_DOMAIN = 'johnatborpa.au.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffeeshop'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code
        # print("AuthError __init__", self.error, self.status_code)


## Auth Header

'''
get_token_auth_header() method
    attempt to get the header from the request
        raise an AuthError if no header is present
    attempt to split bearer and the token
        raise an AuthError if the header is malformed
    return the token part of the header
'''
def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    # attempt to get the header from the request
    auth = request.headers.get('Authorization', None)
    # raise an AuthError if no header is present
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    # attempt to split bearer and the token
    parts = auth.split()
    # raise an AuthError if the header is malformed
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    # return the token part of the header
    token = parts[1]
    # print(token)
    return token

'''
check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT.'
        }, 400)

    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found.'
        }, 401)
    return True

'''
verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    the token should be an Auth0 token with key id (kid)
    verify the token using Auth0 /.well-known/jwks.json
    decode the payload from the token
    validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    # print('a')
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    # print('b')
    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    # print('c')
    if rsa_key:

        algorithms=ALGORITHMS
        audience=API_AUDIENCE
        issuer='https://' + AUTH0_DOMAIN + '/'

        # ### DEBUGGING START
        # print('#### ABOUT TO jwt.decode() START')
        # print('token:',token)
        # print('rsa_key:', rsa_key)
        # print('algorithms:',algorithms)
        # print('audience:',audience)
        # print('issuer:',issuer)

        # print('#### ABOUT TO jwt.decode() END')
        # ### DEBUGGING END


        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )
            return payload

        except jwt.ExpiredSignatureError:
            # print('Token expired.')
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            # print('Incorrect claims. Please, check the audience and issuer.')
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            # print('Unable to parse authentication token.')
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    # print('d')
    raise AuthError({
        'code': 'invalid_header',
        'description': 'Unable to find the appropriate key.'
    }, 400)

'''
@requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    use the get_token_auth_header method to get the token
    use the verify_decode_jwt method to decode the jwt
    use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                token = get_token_auth_header()
                payload = verify_decode_jwt(token)
            except:
                abort(401)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator
