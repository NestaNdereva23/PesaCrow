from django.shortcuts import render, redirect
from django.urls import reverse
from projects.forms import ProjectRequestForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

def projectrequest(request):
    user = request.user
    form = ProjectRequestForm(data=request.POST)
    
    #handle clients project request form
    if request.method == "POST":
        if form.is_valid():
            project_request = form.save(commit=False)
            project_request.user = request.user
            project_request.save()

            #Send email notification to recipient
            subject = f'New project request: {project_request.title}'
            message = f'''

            Hello,

            You have received a new project request from {request.user.username}.

            Project Details:
            Title: {project_request.title}
            Description: {project_request.project_description}
            Budget: Ksh. {project_request.budget}

            Please login to your dashboard to view more details and respond.

            Best regards,
            PesaCrow Team
            '''

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [project_request.receiver_email],
                fail_silently=False,
            )
            
            #handle success message
            messages.success(request, "Project request sent successfully!")
            
            return redirect(reverse("home:dashboard"))
        else:
            print(form.errors)
            messages.error(request, "Project request not sent")
            return redirect(reverse('projects:projectrequest'))
    
    else:
        form= ProjectRequestForm(instance=user)

    context = {"form":form}

    return render(request, "projects/projectrequest.html", context)