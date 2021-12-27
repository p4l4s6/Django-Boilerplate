import json

from django.http import HttpResponse, JsonResponse
from rest_framework.views import exception_handler


def api_500_handler(exception, context):
    response = {
        "status": "error",
        "code": 500,
        "error": exception_handler(exception, context),
        "message": "Internal Server Error! Try again!"
    }
    return JsonResponse(data=response, status=500)
