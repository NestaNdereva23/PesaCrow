
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import authenticate, login , logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404

from pygments.lexers import r
from django.contrib.auth.views import LoginView as AuthLoginView
from django.views.generic import FormView
from django.urls import reverse_lazy, reverse
from .forms import  RegistrationForm
from projects.models import ProjectRequest,Milestone
from contracts.models import Contract
from django.db.models import Count

# Create your views here.
def homepage(request):
    return render(request, 'home/homepage.html')


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

    user = request.user
     #check if fistname and lastname are blanks if so redirect to profile
    if user.first_name == "" and user.last_name == "":
        return redirect(reverse('profiles:profile'))

    context = {}

   #check if user is client
    if user.userprofile.role_type == 'Client':

        try:
            project_requests = ProjectRequest.objects.filter(sender_email=request.user.email, verified=True)
            payment_needed = False
            for project in project_requests:
                    #checkif contract is verified i.e approved by the client after allmilestones have been added
                    if project.verified == True:

                        #check if there is a contract associated with the active project to avoid null error is none exists   
                        if hasattr(project, 'contract') and project.contract is not None:
                                
                            if project.contract.signed_by_client == True and project.contract.signed_by_developer == True:
                                #check for pending miestone
                                pending_milestone = Milestone.objects.filter(
                                    project=project,
                                    status='Pending',
                                    payment_status='Unpaid'
                                    ).order_by('order_number').first()
                            
                                if pending_milestone:
                                    #store the milestone id session for use in payment view
                                    request.session['pending_milestone_id'] = pending_milestone.id
                                    payment_needed=True
                                    break
                        else:
                            #remove any sessions stored if any
                            if 'pending_milestone_id' in request.session:
                                del request.session['pending_milestone_id']
                            
                                return redirect(reverse('home:dashboard'))

            
            if payment_needed:
                 #Prompt payment page with the top milestone to client
                return redirect('payment:milestone_payment')
        except ProjectRequest.DoesNotExist:
            return HttpResponseForbidden("You dont have any project")

    #developer dashboard logic
    elif user.userprofile.role_type == 'Developer':
        try:

            project_requests = ProjectRequest.objects.filter(receiver_email=request.user.email, verified=True)
            
            active_milestones = Milestone.objects.filter(
                            project__in = project_requests, 
                            status='Active'
                            ).order_by('project','order_number')
            
            pending_milestones = Milestone.objects.filter(
                project__in=project_requests,
                status = 'Pending'
            ).order_by('project', 'order_number')

            context = {
                "projects":project_requests,
                "active_milestones":active_milestones,
                "pending_milestones":pending_milestones,
            }
        
        except ProjectRequest.DoesNotExist:
            return HttpResponseForbidden("forbidden")


    return render(request, 'home/dashboard.html', context)


#userlogout view
@login_required
def logoutPage(request):
    logout(request)
    return redirect(reverse('home:home'))


