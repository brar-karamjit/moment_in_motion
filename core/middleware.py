class ForwardedPrefixMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        prefix = request.META.get("HTTP_X_FORWARDED_PREFIX")
        if prefix:
            prefix = prefix.rstrip("/")
            if not prefix.startswith("/"):
                prefix = "/" + prefix
            request.META["SCRIPT_NAME"] = prefix
        return self.get_response(request)
