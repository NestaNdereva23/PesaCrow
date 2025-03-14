from django.db.models import Max
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from projects.forms import ProjectRequestForm, MilestonesForm, EditMilestoneForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from projects.models import ProjectRequest, Milestone
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string


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

    if 'create_milestones' in request.POST:
        return create_milestones(request, project_id)
    else:
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
    if user.userprofile.role_type == 'Developer':
        return developers_projects(request)
    elif user.userprofile.role_type == 'Client':

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
        client_project = get_object_or_404(ProjectRequest, sender_email=request.user.email)
        project = ProjectRequest.objects.filter(id=client_project.id)

        # handle projects for client and developer differently

        if client_project.sender_email == user.email:
            client_projectrequests = ProjectRequest.objects.filter(sender_email=user.email)

            context = {
                "form":form,
                "project": project,
                "client_projectrequests": client_projectrequests,
            }

            return render(request, "projects/projectrequest.html", context)



def create_milestones(request, project_id):
    user = request.user
    project = get_object_or_404(ProjectRequest, id=project_id)
    project_requests = ProjectRequest.objects.filter(receiver_email=request.user.email)
    
    # print(ProjectRequest.objects.filter(receiver_email=request.user.email).query)
    #check for permission
    if project.receiver_email != request.user.email:
        return HttpResponseForbidden("You dont have permission to create milestones for this project.")

    #get existing milestones
    milestones = Milestone.objects.filter(project=project).order_by('order_number')

    #add milestones dynamically using htmx
    if request.method == 'POST' and request.headers.get('HX-Request'):
        form = MilestonesForm(data=request.POST, project=project)
        if form.is_valid():
            milestone = form.save(commit=False)

            if not milestone.order_number:
                last_order = milestones.aggregate(Max('order_number'))['order_number__max'] or 0
                milestone.order_number = last_order + 1

            milestone.save()

            #return only the new html for htmx to insert
            return render(request, "projects/partials/milestone_item.html", {"milestones":milestones})
        else:
            return render(request, "projects/partials/milestone_form.html", {
                "form": form,
                "project": project
            })

    #display milestone_form via htmx
    if request.headers.get('HX-Request') and request.GET.get('action') == 'new_form':
        form = MilestonesForm(project=project)
        return render(request, "projects/partials/milestone_form.html", {
            "form": form,
            "project": project
        })

    #notify client contract is finished
    if request.method == 'POST' and "verify_milestones" in request.POST and project.verified == False:
        #send notification email to sender/client
        send_mail(
            subject=f'Milestone Verification for Project: {project.title}',
            message=
            f'''Hello, the developer {request.user.email} has added milestones to '{project.title}'.
            Visit your project dashboard to verify that the milestones align within your scope.
            . If it aligns click on approve button to generate a contract else communicate with the developer until every milestone aligns
             .''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[project.sender_email],
            fail_silently=False,
        )
        return redirect(reverse('home:dashboard'))
    else:
        return HttpResponseForbidden("Something went wrong when sending notification")

    #default page load
    context = {
        "milestones":milestones,
        "project":project,
        "project_requests":project_requests,
        "new_milestone_form": MilestonesForm(project=project),

    }
    return render(request, "projects/milestones.html", context)


def edit_milestone(request, milestone_id):
    milestone = get_object_or_404(Milestone, id=milestone_id)
    project=milestone.project
    form = EditMilestoneForm(instance=milestone)

    if request.method == "POST":
        form = EditMilestoneForm(data=request.POST, instance=milestone)
        if form.is_valid():
            form.save()
            # return redirect(reverse('projects:milestones', project.id))
            return HttpResponse('<div id="milestone-{}" hx-swap-oob="true">{}</div>'.format(milestone.id, milestone.title))
            # Updates the milestone without full reload
        else:
            return render(request, "projects/partials/edit_milestone_form.html", {"form": form, "milestone": milestone})

    form = EditMilestoneForm(instance=milestone)
    return render(request, "projects/partials/edit_milestone_form.html", {"form": form, "milestone": milestone})


def client_milestone_verification(request, id):
    user = request.user
    project = get_object_or_404(ProjectRequest, id=id)

    # Get milestones for this project
    milestones = Milestone.objects.filter(project=project).order_by('order_number')

    # Check if user is the sender of this project request
    if project.sender_email != user.email:
        return HttpResponseForbidden("You don't have permission to view these milestones")

    # If we get here, user is authorized to see the milestones
    return render(request, "projects/client_milestones.html", {
        "project": project,
        "milestones": milestones
    })