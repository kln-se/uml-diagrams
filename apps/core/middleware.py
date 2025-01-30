import logging

from asgiref.sync import iscoroutinefunction
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.utils.log import log_response
from rest_framework import status

logger = logging.getLogger("django.request")


class CustomExceptionMiddleware(MiddlewareMixin):
    """
    Custom Exception Middleware which returns JSON response
    instead of django's Http exceptions in response.
    """

    def __call__(self, request):
        """
        Overrides parent's __call__ method to use process_exception() method.
        This method change default behavior of HttpResponseNotFound exception
        processing - it returns JsonResponse instead of django's HttpResponseNotFound.
        """
        # Exit out to async mode, if needed
        if iscoroutinefunction(self):
            return self.__acall__(request)
        response = self.get_response(request)
        return self.process_exception(request, response)

    @staticmethod
    def process_exception(_request, response):
        """
        Returns JSON response instead of django's HttpResponseNotFound.
        """
        if isinstance(response, HttpResponseNotFound):
            response = JsonResponse(
                {"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND
            )
        return response


class LogAllRequestsMiddleware(MiddlewareMixin):
    """
    Custom Middleware which force built-in 'django.request' logger to log all requests.
    Because 'django.request' logger logs only 4XX and 5XX responses as a default.
    4ХХ and 5XX responses are still logged by the default django's
    mechanism ('BaseHandler' class in django.core.handlers.base)
    so they won't be logged here.
    """

    def __call__(self, request):
        """
        Overrides parent's __call__ method to use process_response() method.
        Logging other request is enabled if logging level is set to 'INFO'.
        """
        # Exit out to async mode, if needed
        if iscoroutinefunction(self):
            return self.__acall__(request)
        response = self.get_response(request)
        if (
            isinstance(response, HttpResponse)
            and logger.isEnabledFor(logging.INFO)
            and response.status_code < 400
        ):
            return self.process_response(request, response)
        return response

    @staticmethod
    def process_response(request, response):
        """
        This method calls django's log_response() method
        to process request and response data.
        """
        log_response(
            "%s: %s",
            response.reason_phrase,
            request.path,
            response=response,
            request=request,
        )
        return response
