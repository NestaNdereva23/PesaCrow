from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import generic
from django_browser_reload.views import message

from profiles.models import UserProfile, UserRole
from profiles.forms import ProfileUpdateForm, ContactUpdateForm


# Create your views here.
def profiles(request):
    user = request.user
    user_check = User.objects.get(username=request.user)
    if user_check.first_name == "" and user_check.last_name == "":
        messages.warning(request, "Update your profile")

    try:
        user_profile = user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = None

    #userprofile update form
    form_profile = ProfileUpdateForm(data=request.POST, instance=user)
    form_contact = ContactUpdateForm(data=request.POST, instance=user_profile)

    if request.method == "POST":
        if 'formProfile_submit' in request.POST:
            # form_profile = ProfileUpdateForm(data=request.POST, instance=user)
            if form_profile.is_valid():
                form_profile.save()
                return redirect(reverse('home:dashboard'))
        
        elif 'formContact_submit' or 'form_mpesa_number_submit' in request.POST:
            form_contact = ContactUpdateForm(data=request.POST, instance=user_profile)
            if form_contact.is_valid():
                form_contact.save()
                return redirect(reverse('home:dashboard'))

    else:
        form_profile = ProfileUpdateForm(instance=user)
        form_contact = ContactUpdateForm(instance=user_profile)




    context = {
        'user_profile': user_profile,
        'form_profile': form_profile,
        'form_contact': form_contact,
    }


    return render(request, "profiles/profiles.html", context)