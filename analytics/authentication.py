from rest_framework.authentication import SessionAuthentication

class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    SessionAuthentication subclass that does not enforce CSRF validation.
    Used for SPA/Token-based API endpoints so that users browsing Django admin
    do not encounter 'CSRF failed: token missing' in their API calls.
    """
    def enforce_csrf(self, request):
        return  # CSRF validation skipped for API calls using token/session

