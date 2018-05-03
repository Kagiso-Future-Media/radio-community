
class RequestUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            request.user = request.user
        except:
            request.user = 'AnonymousUser'

        response = self.get_response(request)

        return response


class AuthomaticRequestMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.REQUEST = request.GET.dict()
        response = self.get_response(request)
        return response
