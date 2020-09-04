from django.http import HttpResponse
from django.conf import settings
import traceback
import logging
logging.basicConfig()
logger = logging.getLogger('logger')
from django.http.response import Http404
from parlalize.utils_ import Http204


class ErrorHandlerMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if True:
            if type(exception) == Http204:
                print(type(exception))
                logger.error(type(exception))

                return HttpResponse(exception.message, status=204)
