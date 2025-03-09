from django.shortcuts import render


def projectrequest(request):
    return render(request, "projects/projectrequest.html")