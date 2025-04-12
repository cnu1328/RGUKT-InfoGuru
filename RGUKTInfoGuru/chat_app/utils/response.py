from rest_framework.response import Response
from rest_framework import status
from rest_framework.response import Response
from rest_framework import status
import re

class CustomResponse:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensures only a single instance exists (Singleton Pattern).
        """
        if cls._instance is None:
            cls._instance = super(CustomResponse, cls).__new__(cls)
        return cls._instance

    def __call__(self, data=None, message="Success", success=True, status_code=None):
        """
        Returns a formatted API response.

        :param data: The response data (optional).
        :param message: A message describing the response (default: "Success").
        :param success: Boolean indicating success or failure (default: True).
        :param status_code: HTTP status code (default: 200 for success, 400 for error).
        :return: Django Response object.
        """
        status_code = status_code or (status.HTTP_200_OK if success else status.HTTP_400_BAD_REQUEST)

        return Response({
            "message": message,
            "data": data,
            "status_code": status_code
        }, status=status_code)


def remove_think_tags(text):
        pattern = r'<think>.*?</think>'
        cleaned_text = re.sub(pattern, '', text, flags=re.DOTALL)
        return cleaned_text.strip()