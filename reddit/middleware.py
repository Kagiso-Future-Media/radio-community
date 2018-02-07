
class RequestUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            request.user = request.user
        except:
            request.user = 'AnonymousUser'
        print('=========================================')
        print(request.user)
        response = self.get_response(request)

        return response

# class RequestTestMiddleware:
#     def process_request(self, request):
#         try:
#             request.user = request.user
#         except:
#             request.user = 'AnonymousUser'
#         print('=========================================')
#         print(request.user)



# class SimpleMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
#         # One-time configuration and initialization.
#
#     def __call__(self, request):
#         # Code to be executed for each request before
#         # the view (and later middleware) are called.
#
#         response = self.get_response(request)
#
#         # Code to be executed for each request/response after
#         # the view is called.
#
#         return response