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
from contracts.models import Contract
from contracts.services import create_contract_from_template

#handle the recepient of the project request view
@login_required
def developers_projects(request):
    user = request.user
    project_requests = ProjectRequest.objects.filter(receiver_email=user.email)

    project_progress = []

    for project in project_requests:
        milestones = Milestone.objects.filter(project=project)
        completed_milestones = Milestone.objects.filter(project=project, status="Completed").count()
        total_milestones = Milestone.objects.filter(project=project).count()

        if total_milestones > 0:
            milestone_percentage = (completed_milestones / total_milestones ) *  100
        else:
            milestone_percentage = 0

        project_progress.append({
            'project': project,
            'milestones': milestones,
            'completed_milestones':completed_milestones,
            'total_milestones':total_milestones,
            'milestone_percentage':milestone_percentage
        })
    # print(Milestone.objects.filter(project_requests, status="completed").query)
    context = {
        'project_progress':project_progress
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
            # send_mail(
            #     subject = f'Your project has been accpeted',
            #     message = f"Hello, your project '{project.title}' has been accepted by {request.user.email}.",
            #     from_email=settings.DEFAULT_FROM_EMAIL,
            #     recipient_list=[project.sender_email],
            #     fail_silently=False,
            # )
            return redirect(reverse('home:dashboard'))

#client project request handling
def projectrequest(request):
    user = request.user
    if user.userprofile.role_type == 'Developer':
        return developers_projects(request)
    
    elif user.userprofile.role_type == 'Client':
        form = ProjectRequestForm(data=request.POST or None)

        if request.method == "POST":
            if form.is_valid():
                project_request = form.save(commit=False)
                project_request.sender_email = user.email
                project_request.user = request.user
                project_request.save()

                # Send email notification to recipient
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

                # send_mail(
                #     subject,
                #     message,
                #     settings.DEFAULT_FROM_EMAIL,
                #     [project_request.receiver_email],
                #     fail_silently=False,
                # )

                messages.success(request, "Project request sent successfully!")
                return redirect(reverse("home:dashboard"))
            else:
                print(form.errors)
                messages.error(request, "Project request not sent")
                return redirect(reverse('projects:projectrequest'))
        else:
            form = ProjectRequestForm()

        # Filter sent project request
        client_project = ProjectRequest.objects.filter(sender_email=request.user.email).first()
        project = ProjectRequest.objects.filter(id=client_project.id) if client_project else None

        # Handle projects for client and developer differently
        project_requests = ProjectRequest.objects.filter(sender_email=user.email)

        project_progress = []

        for project in project_requests:
            milestones = Milestone.objects.filter(project=project)
            completed_milestones = Milestone.objects.filter(project=project, status="Completed").count()
            total_milestones = Milestone.objects.filter(project=project).count()

            if total_milestones > 0:
                milestone_percentage = (completed_milestones / total_milestones) * 100
            else:
                milestone_percentage = 0

            project_progress.append({
                'project': project,
                'milestones': milestones,
                'completed_milestones': completed_milestones,
                'total_milestones': total_milestones,
                'milestone_percentage': milestone_percentage
            })
        print(project_progress)
        context = {
            "form": form,
            "project": project,
            'project_progress': project_progress
        }

        return render(request, "projects/projectrequest.html", context)

""" Allows the developer to create milestones after they have accepted the project request from the client"""
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


    #notify client the milestones are done 
    if request.method == 'POST' and "verify_milestones" in request.POST:
        if not project.verified:
            #send notification email to sender/client after the developer has finished creating the milestones
            # send_mail(
            #     subject=f'Milestone Verification for Project: {project.title}',
            #     message=f'''
            #     Hello, the developer {request.user.email} has added milestones to '{project.title}'.\n
            #     Visit your project dashboard to verify that the milestones align within your scope.\n
            #     .If it aligns click on approve button to generate a contract else communicate with the developer until every milestone aligns.
            #     ''',
            #     from_email=settings.DEFAULT_FROM_EMAIL,
            #     recipient_list=[project.sender_email],
            #     fail_silently=False,
            # )
            return redirect(reverse('home:dashboard'))

    #default page load
    context = {
        "milestones":milestones,
        "project":project,
        "project_requests":project_requests,
        "new_milestone_form": MilestonesForm(project=project),

    }
    return render(request, "projects/milestones.html", context)

# developers edit the milestones 
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


""" allows client to view and approve milestones added/updated  by developer """
def client_milestone_verification(request, id):
    user = request.user
    project = get_object_or_404(ProjectRequest, id=id)

    # Get milestones for this project
    milestones = Milestone.objects.filter(project=project).order_by('order_number')

    # Check if user is the sender of this project request
    if project.sender_email != user.email:
        return HttpResponseForbidden("You don't have permission to view these milestones")

    if request.method == 'POST' and "approve_milestones" in request.POST:
        if not project.verified: #check to ensure project is not verified , if it is verified ot has already been approved
        
            project.verified = True    # approve project verification status
            project.save()
            #send notification email to the developer for approving the milestones  added to the project
            # send_mail(
            #     subject=f'Milestone Verification for Project: {project.title}',
            #     message=f'''
            #             Hello, the client {project.sender_email} approved '{project.title}' and the added milestones.\n
            #             Everything seems fine. Check you contracts section to proceed.\n
            #
            #             Best regards,\n
            #             PesaCrow Team :)
            #             ''',
            #     from_email=settings.DEFAULT_FROM_EMAIL,
            #     recipient_list=[project.receiver_email],
            #     fail_silently=False,
            # )
            # Check if a contract already exists for this project
            try:
                contract = Contract.objects.get(project=project)
                # If contract exists, redirect to edit contraacts page
                return redirect('contracts:edit_contract', contract_id=contract.id)
            except Contract.DoesNotExist:
                # If no contract exists, create one first
                from django.core.management import call_command
                call_command('initialize_contract_templates')    #initialize templates if not already initialized
                contract = create_contract_from_template(project.id)
                return redirect('contracts:edit_contract', contract_id=contract.id)
        else:
             #TODO  check the project status
             project_status = project.status
             messages.info(request, f"{project_status}")


    elif  request.method == 'POST' and "disapprove_milestones" in request.POST:
        if not project.verified:
            # send_mail(
            #     subject=f'Milestone Verification for Project: {project.title}',
            #     message=f'''
            #                     Hello, the client {project.sender_email} disapproved some sections of the milestones.\n
            #                     Consult with the client to address the issues.\n

            #                     Best regards,\n
            #                     PesaCrow Team :)
            #                     ''',
            #     from_email=settings.DEFAULT_FROM_EMAIL,
            #     recipient_list=[project.receiver_email],
            #     fail_silently=False,
            # )
            return redirect(reverse('home:dashboard'))

    # user is authorized to see the milestones
    return render(request, "projects/client_milestones.html", {
        "project": project,
        "milestones": milestones
    })


