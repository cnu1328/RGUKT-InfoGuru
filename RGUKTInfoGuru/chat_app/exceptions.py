from rest_framework.exceptions import APIException
from rest_framework import status

class CustomException(APIException):
    default_status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, detail, status_code=None):
        self.status_code = status_code if status_code is not None else self.default_status_code
        self.detail = detail