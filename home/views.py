from typing import Any

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views import View
from pygments.lexers import r
from django.contrib.auth.views import LoginView as AuthLoginView
from django.views.generic import FormView
from django.urls import reverse_lazy, reverse
from .forms import  RegistrationForm

# Create your views here.
def homepage(request):
    return render(request, 'home/homepage.html')

# def registration(request):
#     form = RegistrationForm(request.POST or None)

#     if request.method == "POST":
#         form = RegistrationForm(request.POST or None)
#         if form.is_valid():
#             form.save()
#             # user = form.cleaned_data.get('email')
#             return reverse('login')

#     return render(request, 'registration/registration.html', {'form': form})

class RegistrationView(FormView):
    template_name = 'registration/registration.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('home:login')

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST or None)
        if form.is_valid():
            #process form data
            user = form.save()
            if user:
                return redirect(self.success_url)
            
        return render(request, self.template_name, {'form': form})





def login_page(request):

    if request.method == "POST":
        # email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        # user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect(reverse('home:dashboard'))
        else:
            messages.warning(request, 'Email or password is incorrect')

    return render(request, 'registration/login.html')


#user dashboard view
@login_required
def dashboard(request):
    #check if fistname and lastname are blanks if so redirect to profile
    user = User.objects.get(username=request.user)

    if user.first_name == "" and user.last_name == "":
        return redirect(reverse('profiles:profile'))

    return render(request, 'home/dashboard.html')


