import json
import logging
import logging.config
import os
from flask import request, abort, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Set up logging
logging.config.fileConfig(fname='logfile.conf', disable_existing_loggers=False)
# Get the logger specified in the file
logger = logging.getLogger(__name__)
logger.debug('STARTING the Coffee Shop auth.py module')

AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN', 'johnatborpa.au.auth0.com')
API_AUDIENCE = os.getenv('API_AUDIENCE', 'coffeeshop')
ALGORITHM = os.getenv('ALGORITHM', 'RS256')
ALGORITHMS = [ALGORITHM]

# # ### DEBUGGING START
# logger.debug('#### ABOUT TO SHOW ENVIRONMENT VARIABLES START')
# logger.debug('algorithms:%s:', ALGORITHMS)
# logger.debug('audience:%s:', API_AUDIENCE)
# logger.debug('domain:%s:', AUTH0_DOMAIN)
# logger.debug('#### ABOUT TO SHOW ENVIRONMENT VARIABLES END')
# # ### DEBUGGING END


class AuthError(Exception):
    '''
    AuthError Exception. A standardized way to communicate auth failure modes.
    '''
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code
        logger.debug("AuthError __init__ %s %s", self.error, self.status_code)


def get_token_auth_header():
    """
    Obtains the Access Token from the Authorization Header.

    Attempts to get the header from the request
        raises an AuthError if no header is present.

    Attempts to split bearer and the token
        raises an AuthError if the header is malformed.

    Returns the token part of the header.
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
    # logger.debug("Token is [[[%s]]]", token)
    return token


def check_permissions(permission, payload):
    '''
    Checks that the user has the appropriate remissions in the JWT.

    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    Raises an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0

    Raise an AuthError if the requested permission string is not in the
    payload permissions array.

    Returns True otherwise.
    '''
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


def verify_decode_jwt(token):
    '''
    Extracts the Bearer Token from the header and decodes the payload.

    @INPUTS
        token: a json web token (string)

    The token should be an Auth0 token with key id (kid).

    Verifies the token using Auth0 /.well-known/jwks.json

    Decodes the payload from the token.

    Validates the claims.

    Returns the decoded payload

    !!NOTE urlopen has a common certificate error described here:
    https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
    '''
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    # logger.debug('a')
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    # logger.debug('b')
    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    # logger.debug('c')
    if rsa_key:
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
            logger.debug('Token expired.')
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            logger.debug('Incorrect claims. Check the audience and issuer.')
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Check audience and issuer.'
            }, 401)
        except Exception:
            logger.debug('Unable to parse authentication token.')
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    # logger.debug('d')
    raise AuthError({
        'code': 'invalid_header',
        'description': 'Unable to find the appropriate key.'
    }, 400)


def requires_auth(permission=''):
    '''
    @requires_auth(permission) decorator method.

    @INPUTS
        permission: string permission (i.e. 'post:drink')

    Uses the get_token_auth_header method to get the token.

    Uses the verify_decode_jwt method to decode the jwt.

    Uses the check_permissions method to validate claims and
    check the requested permission.

    Returns the decorator which passes the decoded payload to the
    decorated method.
    '''
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator
