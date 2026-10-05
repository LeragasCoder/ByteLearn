from django.conf import settings


class PreviewOriginMiddleware:
    """در حالت توسعه، Origin درخواست را برای CSRF می‌پذیرد."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.DEBUG:
            origin = request.META.get("HTTP_ORIGIN")
            trusted = settings.CSRF_TRUSTED_ORIGINS
            if origin and origin not in trusted:
                trusted.append(origin)
        return self.get_response(request)
