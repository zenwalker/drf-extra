from rest_framework.authentication import BaseAuthentication


class SessionAuthentication(BaseAuthentication):
    def authenticate(self, request):
        request = request._request
        user = getattr(request, 'user', None)

        if not user or not user.is_active:
            return None

        return (user, None)
