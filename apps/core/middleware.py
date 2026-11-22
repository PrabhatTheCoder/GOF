PRIVATE_PREFIXES = (
    "/student/",
    "/staff/",
    "/login/",
    "/logout/",
    "/api/",
    "/admin/",
    "/django-admin/",
)


class PrivateNoIndexMiddleware:
    """Keep private areas out of search indexes, even for non-HTML responses."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith(PRIVATE_PREFIXES):
            response["X-Robots-Tag"] = "noindex, nofollow"
        return response
