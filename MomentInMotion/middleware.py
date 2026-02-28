from django.conf import settings


class ForwardedPrefixMiddleware:
    """Respect reverse proxy prefix headers for correct URL generation."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        prefix = request.META.get("HTTP_X_FORWARDED_PREFIX") or settings.FORCE_SCRIPT_NAME
        if prefix:
            if not prefix.startswith("/"):
                prefix = "/" + prefix

            if request.path_info.startswith(prefix):
                request.META["SCRIPT_NAME"] = prefix
                request.META["PATH_INFO"] = request.path_info[len(prefix):] or "/"
            else:
                request.META.setdefault("SCRIPT_NAME", prefix)

        return self.get_response(request)
