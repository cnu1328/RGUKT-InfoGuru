from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

# Create your views here.
def home(request):
    return HttpResponse("Created simple page!!")
