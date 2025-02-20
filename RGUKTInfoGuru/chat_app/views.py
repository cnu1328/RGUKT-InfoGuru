from django.shortcuts import render
from rest_framework.views import APIView

# Create your views here.

from rest_framework.views import APIView
from .utils.response import CustomResponse


class TestView(APIView):
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Implements the Singleton pattern to ensure only one instance is created.
        """
        if cls._instance is None:
            cls._instance = super(TestView, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        """
        Initializes the TestView instance if it hasn't been initialized yet.
        Ensures that initialization only happens once.
        """
        if not hasattr(self, "initialized"):
            super().__init__(**kwargs)
            self.initialized = True
            self.Response = CustomResponse()

    def get(self, request):
        return self.Response()
