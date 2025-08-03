from .forms import DisputeForm, DisputeMessageForm, EvidenceForm, RulingForm
from .models import Dispute,Deliverable,Milestone, DisputeMessage, Evidence, DECISION_CHOICES
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from django.db.models import Q
from payment.services import release_funds

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

def dispute_detail(request, dispute_id):
    dispute = get_object_or_404(Dispute, id=dispute_id)
    dispute_messages = DisputeMessage.objects.filter(dispute=dispute)
    evidence_list = Evidence.objects.filter(dispute=dispute)

    if request.method == 'POST':
        message_form = DisputeMessageForm(request.POST)
        evidence_form = EvidenceForm(request.POST, request.FILES)
        ruling_form = RulingForm(request.POST)

        if 'submit_message' in request.POST and message_form.is_valid():
            message = message_form.save(commit=False)
            message.dispute = dispute
            message.sender = request.user
            message.save()
            return redirect('disputes:dispute_detail', dispute_id=dispute.id)

        if 'submit_evidence' in request.POST and evidence_form.is_valid():
            evidence = evidence_form.save(commit=False)
            evidence.dispute = dispute
            evidence.uploader = request.user
            evidence.save()
            return redirect('disputes:dispute_detail', dispute_id=dispute.id)

        if 'submit_ruling' in request.POST and ruling_form.is_valid() and request.user.is_superuser:
            decision = ruling_form.cleaned_data['decision']
            justification = ruling_form.cleaned_data['justification']

            dispute.status = 'resolved_by_admin'
            dispute.decision = decision
            dispute.resolved_at = timezone.now()
            dispute.save()

            # Add justification as a message from the admin
            DisputeMessage.objects.create(
                dispute=dispute,
                sender=request.user,
                message=f"**Admin Ruling:** {dict(DECISION_CHOICES)[decision]}\n\n{justification}"
            )

            # Automated fund release logic
            if decision == 'developer_favored':
                release_funds(dispute.raised_against.userprofile.phone_number, dispute.milestone.payment_amount)
            elif decision == 'client_favored':
                release_funds(dispute.raised_by.userprofile.phone_number, dispute.milestone.payment_amount)

            messages.success(request, f"Dispute resolved. Decision: {decision}")
            return redirect('disputes:dispute_detail', dispute_id=dispute.id)

    else:
        message_form = DisputeMessageForm()
        evidence_form = EvidenceForm()
        ruling_form = RulingForm()

    context = {
        'dispute': dispute,
        'dispute_messages': dispute_messages,
        'evidence_list': evidence_list,
        'message_form': message_form,
        'evidence_form': evidence_form,
        'ruling_form': ruling_form,
    }
    return render(request, 'disputes/dispute_detail.html', context)
