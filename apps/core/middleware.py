from asgiref.sync import iscoroutinefunction
from django.http import HttpResponseNotFound, JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status


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
