from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from django.utils import timezone
from django.db import transaction
from .models import Milestone, Deliverable, DeliverableReview
from .forms import DeliverableSubmissionForm, DeliverableReviewForm


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
    user = request.user
    available_deliverables = Deliverable.objects.filter()
    client_deliverables = Deliverable.objects.filter(
        milestone__project__sender_email=request.user.email,
        status__in=['pending', 'approved', 'revision_requested', 'rejected', 'dispute_raised']
    ).select_related('milestone', 'milestone__project', 'developer')

    context = {
        "available_deliverables": available_deliverables,
        "client_deliverables":client_deliverables,
    }
    return render(request, "deliverables/deliverables_list.html", context)

def review_deliverables(request, deliverable_id):
    submitted_deliverables = Deliverable.objects.filter(
        status="pending",
        milestone__project__sender_email=request.user.email
    ).select_related('milestone', 'milestone__project','developer')
    print(submitted_deliverables)
    if request.method == "POST":
        deliverable_id = request.POST.get('deliverable_id')
        decision = request.POST.get('reviewDecision')
        comments = request.POST.get('reviewComments', '').strip()

        deliverable = get_object_or_404(
            Deliverable,
            id=deliverable_id,
            status="pending",
            milestone__project__sender_email=request.user.email,

        )
        print(deliverable)
        # Map form values to model choices
        status_mapping = {
            'approve': 'approved',
            'revisions': 'revision_requested',
            'reject': 'rejected'
        }
        new_status = status_mapping.get(decision)
        if not new_status:
            messages.error(request, "Invalid review decision.")
            return render(request, "deliverables/deliverables_list.html", {
                "submitted_deliverables": submitted_deliverables,
            })

        try:
            with transaction.atomic():
                # Update the deliverable status and comments
                deliverable.status = new_status
                deliverable.reviewer_comments = comments
                deliverable.reviewed_at = timezone.now()
                deliverable.save()

                # Create a review record for history tracking
                DeliverableReview.objects.create(
                    deliverable=deliverable,
                    reviewer=request.user,
                    decision=new_status,
                    comments=comments
                )

                # Success message based on decision
                if new_status == 'approved':
                    milestone = deliverable.milestone
                    milestone.status = "Completed"
                    milestone.save()
                    messages.success(request, f"Deliverable '{deliverable.title}' has been approved. Funds will be released to the developer")
                elif new_status == 'revision_requested':
                    messages.info(request, f"Revision requested for deliverable '{deliverable.title}'.")
                else:  # rejected
                    messages.warning(request, f"Deliverable '{deliverable.title}' has been rejected.")

                return redirect(reverse('home:dashboard'))
        except Exception as e:
            messages.error(request, f"An error occurred while processing your review: {str(e)}")
    deliverable = Deliverable.objects.select_related(
        'milestone', 'milestone__project', 'developer'
    ).get(id=deliverable_id)  # use your id, e.g., 2

    context = {
        # "deliverables": submitted_deliverables,
        'deliverable':deliverable
    }
    return render(request, "deliverables/deliverable_review.html", context)
