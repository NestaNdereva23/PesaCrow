from django.shortcuts import render
from django.views import generic


# Create your views here.
def profiles(request):
    return render(request, "profiles/profiles.html")