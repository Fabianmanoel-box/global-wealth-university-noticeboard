from django.contrib.sites.models import Site


class DynamicSiteDomainMiddleware:
    """
    Auto-updates the Site domain based on incoming request host.
    Ensures password reset links use the correct domain on local + production.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        try:
            site = Site.objects.get(id=1)
            if site.domain != host:
                site.domain = host
                site.name = 'Global Wealth University Notice Board'
                site.save()
        except Site.DoesNotExist:
            pass

        return self.get_response(request)