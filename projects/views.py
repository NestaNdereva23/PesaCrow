from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from projects.forms import ProjectRequestForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from projects.models import ProjectRequest
from django.contrib.auth.decorators import login_required


#handle the recepient of the project request view
@login_required
def developers_projects(request):
    user = request.user
    project_requests = ProjectRequest.objects.filter(receiver_email=request.user.email)
    # print(ProjectRequest.objects.filter(receiver_email=request.user.email).query)
    
    context = {
        "project_requests":project_requests,
    }
    return render(request, "projects/developers_projects.html", context)


'''
    Accept project change status from pending to active
    Send notification email to client when developer accepts the 
    project request sent.
'''
@login_required
def accept_project(request, project_id):
    project = get_object_or_404(ProjectRequest, id=project_id, receiver_email=request.user.email)

    if project.status == 'Pending':
        project.status  = 'Active'
        project.save()

        #send email to client
        send_mail(
            subject = f'Your project has been accpeted',
            message = f"Hello, your project '{project.title}' has been accepted by {request.user.email}.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[project.sender_email],
            fail_silently=False,
        )

        return redirect(reverse('home:dashboard'))

    

#client project request handling
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

    #filter sent project request
    client_projectrequests = ProjectRequest.objects.filter(user=request.user)
    

    context = {
        "form":form,
        "client_projectrequests": client_projectrequests,
    }

    #handle projects for client and developer differently
    if user.userprofile.role_type == 'Client':
        return render(request, "projects/projectrequest.html", context)
    elif user.userprofile.role_type == 'Developer':
        return developers_projects(request)


