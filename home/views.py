from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views import View
from pygments.lexers import r

#testing
from django.template.loader import get_template
from django.http import HttpResponse

from .forms import  RegistrationForm

# Create your views here.
def homepage(request):
    return render(request, 'home/homepage.html')

def login_page(request):

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.warning(request, 'Email or password is incorrect')

    return render(request, 'registration/login.html')

def registration(request):
    form = RegistrationForm(request.POST or None)

    if request.method == "POST":
        form = RegistrationForm(request.POST or None)
        if form.is_valid():
            form.save()
            # user = form.cleaned_data.get('email')
            return redirect('login')

    return render(request, 'registration/registration.html', {'form': form})

