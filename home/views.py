
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
from django.views.generic import TemplateView
from django.db.models import Count, Sum, Q
from disputes.models import Dispute, Deliverable
# Create your views here.
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def admin_dashboard_view(request):
    # Placeholder summary data for now
    context = {
        'disputes_count': 0,
        'fund_release_count': 0,
        'project_count': 0,
        'alerts_count': 0,
    }
    return render(request, 'home/admin_dashboard.html', context)

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
def dashboard_view(request):
    user = request.user
    if user.is_superuser:
        return redirect(reverse('home:admin_dashboard'))
    #check if user has a profile
    if not hasattr(user, 'userprofile'):
        return redirect(reverse('profiles:profile'))

    profile = user.userprofile
    is_client = profile.role_type == 'Client'

    if is_client:
        active_projects = ProjectRequest.objects.filter(user=user, status='Active')
    else:
        active_projects = ProjectRequest.objects.filter(receiver_email=user.email, status='Active')


    active_projects_data = []
    for project in active_projects:
        milestones = project.project_milestones.all()
        total = milestones.count()
        completed = milestones.filter(status='Completed').count()
        progress = int((completed / total) * 100) if total > 0 else 0

        active_projects_data.append({
            'project': project,
            'total': total,
            'completed': completed,
            'progress': progress,
        })

    pending_milestones = Milestone.objects.filter(
        project__in=active_projects, status='Pending'
    )

    escrow_total = Milestone.objects.filter(
        project__in=active_projects, payment_status='Paid'
    ).aggregate(total=Sum('payment_amount'))['total'] or 0

    disputes = Dispute.objects.filter(
        Q(raised_by=user) | Q(raised_against=user)
    )

    pending_reviews = Deliverable.objects.filter(
        milestone__project__receiver_email=user.email,
        status='pending'
    ) if not is_client else []

    context = {
        'active_projects': active_projects,
        'active_projects_data': active_projects_data,
        'pending_milestones': pending_milestones,
        'escrow_total': escrow_total,
        'disputes': disputes,
        'pending_reviews': pending_reviews,
    }
    return render(request, 'home/dashboard.html', context)


#userlogout view
@login_required
def logoutPage(request):
    logout(request)
    return redirect(reverse('home:home'))


def escrow_account(request):
    pass


@staff_member_required
def admin_disputes(request):
    escalated_disputes = Dispute.objects.filter(status='escalated')
    context = {
        'disputes': escalated_disputes,
    }
    return render(request, 'home/admin_disputes.html', context)
