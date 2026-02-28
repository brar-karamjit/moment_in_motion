from django.conf import settings
from django.urls import set_script_prefix


class ForwardedPrefixMiddleware:
    """Honour the X-Forwarded-Prefix header (or FORCE_SCRIPT_NAME) so that
    reverse(), {% url %}, request.path, and login redirects all include
    the sub-path prefix set by the reverse-proxy / Ingress."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        prefix = (
            request.META.get("HTTP_X_FORWARDED_PREFIX")
            or settings.FORCE_SCRIPT_NAME
            or ""
        )
        if prefix:
            prefix = "/" + prefix.strip("/")

            # 1. WSGI environ — some Django internals read SCRIPT_NAME here
            request.META["SCRIPT_NAME"] = prefix

            # 2. Thread-local script prefix — used by reverse() and {% url %}
            set_script_prefix(prefix)

            # 3. request.path — used by get_full_path() which sets the
            #    ?next= parameter on login redirects.  FORCE_SCRIPT_NAME
            #    may have already prepended the prefix during WSGIRequest
            #    init, so guard against doubling it.
            if not request.path.startswith(prefix):
                request.path = prefix + request.path

        return self.get_response(request)
