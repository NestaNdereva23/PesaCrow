from .forms import DisputeForm
from .models import Dispute,Deliverable,Milestone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from django.db.models import Q

# Create your views here.
def disputes_list(request):
    user = request.user
    disputes = Dispute.objects.filter(Q(raised_by=user) | Q(raised_against=user)).order_by('-created_at')
    print(disputes)
    context = {
        'disputes':disputes,
    }
    return render(request, 'disputes/disputes_list.html', context)
def raise_dispute(request, dispute_id):
    deliverable = get_object_or_404(Deliverable, id=dispute_id)
    milestone = deliverable.milestone

    if request.user == deliverable.developer:
        partyB = milestone.project.user
    else:
        partyB = deliverable.developer

    if request.method == 'POST':
        form = DisputeForm(request.POST)
        if form.is_valid():
            dispute = form.save(commit=False)
            dispute.deliverable = deliverable
            dispute.milestone = milestone
            dispute.raised_by = request.user
            dispute.raised_against = partyB
            dispute.escalation_deadline = timezone.now() + timedelta(hours=48)
            deliverable.status = 'disputed'
            dispute.save()

            #send notification
            messages.success(request, "Dispute raised successfully. The other party has been notofied")
            return redirect(reverse('disputes:disputes_list'))
    else:
        form = DisputeForm()

    context = {
        'form': form,
        'deliverable': deliverable,
        'milestone':milestone,
    }
    return render(request, 'disputes/raise_dispute.html', context)

@login_required
def resolve_dispute(request, dispute_id):
    '''
    Allows either party involved in an open dispute to mark it as resolved by parties
    :param request:
    :param dispute_id:
    :return:
    '''
    dispute = get_object_or_404(Dispute, id=dispute_id)

    #check if current user is part of this dispute
    if request.user != dispute.raised_by and request.user != dispute.raised_against:
        messages.error(request, "You are not authorized to resolve this dispute")
        return redirect(reverse('disputes:disputes_list'))

    #Allow resolution only if the dispute is currently 'open'
    if dispute.status == 'open':
        dispute.status = 'resolved_by_parties'
        dispute.resolved_at = timezone.now()
        dispute.save()
        messages.success(request, "Dispute marked as 'Resolved by Parties'")
    else:
        messages.warning(request, f"This dispute is not 'open' and cannot be resolved by parties")

    return redirect(reverse('disputes:disputes_list'))

@login_required
def escalate_dispute_manually(request, dispute_id):
    '''
    Allows either party to manually eacalate an 'open' dispute to the admin before
    48hours elapses or if they decide it's irreconcilable
    '''
    dispute = get_object_or_404(Dispute, id=dispute_id)

    #check if current user is part of this dispute
    if request.user != dispute.raised_by and request.user != dispute.raised_against:
        messages.error(request, "You are not authorized to resolve this dispute")
        return redirect(reverse('disputes:disputes_list'))

    #Allow resolution only if the dispute is currently 'open'
    if dispute.status == 'open':
        dispute.status = 'escalated'
        dispute.is_escalated = True
        dispute.save()
        messages.info(request, "Dispute manually escalated to Admin for review")
    else:
        messages.warning(request, f"This dispute is not 'open' and cannot be manually escalated. Current status: {dispute.get_status_display()}.")

    return redirect(reverse('disputes:disputes_list'))


































