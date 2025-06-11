from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.db import transaction
import json
import mimetypes
import os

from .models import Milestone, Deliverable, DeliverableReview
from .forms import DeliverableSubmissionForm


''' Handle deliverable submission from developer to client'''
@login_required
def submit_deliverable(request, milestone_id):
    milestone = get_object_or_404(Milestone, id=milestone_id)

    if request.method == 'POST':
        form = DeliverableSubmissionForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                deliverable = form.save(commit=False)
                deliverable.milestone = milestone
                deliverable.developer = request.user
                deliverable.submission_link = request.POST.get('submission_link')
                deliverable.save()

                # send_deliverable_notification(deliverable)
                messages.success(request, "Deliverable submitted successfully! The client will be notified for review.")
                return redirect('deliverables:milestone_detail', milestone_id=milestone.id)
    else:
        form = DeliverableSubmissionForm()

    context = {
        'form':form,
        'milestone':milestone
    }
    return render(request, 'deliverables/submit_deliverable.html', context)

# def send_deliverable_notification(request, deliverable):
#     """Send email notification to client when deliverable is submitted"""
#     subject = f"New Deliverable Ready for Review - {deliverable.milestone.project.title}"
    
#     # Get client email
#     client_email = deliverable.milestone.project.receiver_email
    
#     # Create email content
#     context = {
#         'deliverable': deliverable,
#         'milestone': deliverable.milestone,
#         'project': deliverable.milestone.project,
#         'review_url': request.build_absolute_uri(deliverable.get_review_url()) if hasattr(request, 'build_absolute_uri') else f"{settings.SITE_URL}{deliverable.get_review_url()}",
#     }
    
#     html_message = render_to_string('deliverables/emails/deliverable_submitted.html', context)
#     plain_message = render_to_string('deliverables/emails/deliverable_submitted.txt', context)
    
#     try:
#         send_mail(
#             subject=subject,
#             message=plain_message,
#             html_message=html_message,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[client_email],
#             fail_silently=False,
#         )
#     except Exception as e:
#         print(f"Failed to send email: {e}")


""" Clients deliverables i.e active, underreview"""
def deliverables_list(request):
    available_deliverables = Deliverable.objects.filter()
    context = {
        "available_deliverables": available_deliverables,
    }
    return render(request, "deliverables/deliverables_list.html", context)