from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from urllib.parse import parse_qs


@database_sync_to_async
def get_user_from_token(token_key):
    """Get user from token"""
    try:
        token = Token.objects.select_related('user').get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware(BaseMiddleware):
    """
    Custom middleware for token authentication in WebSocket connections.
    Extracts token from query parameters and authenticates the user.
    """
    
    async def __call__(self, scope, receive, send):
        # Get query string from scope
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        
        # Extract token from query parameters
        token_key = query_params.get('token', [None])[0]
        
        if token_key:
            # Authenticate user with token
            scope['user'] = await get_user_from_token(token_key)
        else:
            # No token provided, set as anonymous user
            scope['user'] = AnonymousUser()
        
        return await super().__call__(scope, receive, send)


def TokenAuthMiddlewareStack(inner):
    """
    Wrapper function to apply TokenAuthMiddleware
    Usage: TokenAuthMiddlewareStack(URLRouter(...))
    """
    return TokenAuthMiddleware(inner)
