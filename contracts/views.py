from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.forms import modelformset_factory
from django.urls import reverse
from .models import ProjectRequest, Contract, ContractSection
from .services import create_contract_from_template
from .forms import ContractSectionForm
from django.core.management import call_command
from projects.models import Milestone



def ensure_contract_templates_exist():
    call_command('initialize_contract_templates')

@login_required
def contract(request):
    user=request.user

    if user.userprofile.role_type == 'Client':
        project_requests = ProjectRequest.objects.filter(sender_email=request.user.email, verified=True)
        # if request.method == 'POST':
        #     return redirect(reverse('contracts:edit_contract'))

        context = {"project": project_requests, "contract": contract}
        return render(request, "contracts/contracts.html", context)
    elif user.userprofile.role_type == 'Developer':
        project_requests = ProjectRequest.objects.filter(receiver_email=request.user.email, verified=True)
        context = {"project": project_requests}
        return render(request, "contracts/contracts.html", context)


@login_required
def generate_contract(request, project_id):
    project = get_object_or_404(ProjectRequest, id=project_id)

    if request.user.email != project.sender_email and request.user.email != project.receiver_email:
        return HttpResponseForbidden("You dont have access to this project")
    
    #check if contract exists
    try:
        contract = Contract.objects.get(project=project)
    except Contract.DoesNotExist:
        contract = create_contract_from_template(project_id)

    return redirect(reverse('contracts:edit_contract'), contract_id=contract.id)

@login_required
def edit_contract(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    project = contract.project

    if request.user.email != project.sender_email and request.user.email != project.receiver_email:
        return HttpResponseForbidden("You dont have access to this contract")
 
    editable_sections = contract.sections.filter(editable=True).order_by('order')
    fixed_sections = contract.sections.filter(editable=False).order_by('order')

    #create formsets for editable sections
    SectionFormSet = modelformset_factory(
        ContractSection,
        form=ContractSectionForm,
        extra=0
    )

    if request.method == 'POST':
        formset = SectionFormSet(request.POST, queryset=editable_sections)

        if formset.is_valid():
            formset.save()
            messages.success(request, "Contract update successfully")
            print("workinggggggggggggggggggg")
            return redirect(reverse('contracts:review_contract'), contract_id=contract.id)
        else:
            print(formset.errors)

    else:
        formset = SectionFormSet(queryset=editable_sections)

    context = {'contract':contract, 
               'project':project, 
               'formset':formset, 
               'fixed_sections':fixed_sections}

    return render(request, "contracts/edit_contract.html", context)


@login_required
def review_contract(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    project = contract.project

    if request.user.email != project.sender_email and request.user.email != project.receiver_email:
        return HttpResponseForbidden("You dont have access to this contract")
 
    if request.method == 'POST':
        #handle signing logic
        now = timezone.now()
        if request.user.email == project.sender_email:
            contract.signed_by_client = True
            contract.client_signature_date = now

        elif request.user.email == project.receiver_email:
            contract.signed_by_developer = True
            contract.developer_signature_date = now

        contract.save()
        messages.success(request, "Contract signed successfully")
        return redirect(reverse('home:dashboard'))

    #get all sections in order
    sections = contract.sections.all().order_by('order')

    context = {'contract':contract, 'sections':sections, 'project':project }    

    return render(request, 'contracts/review_contract.html', context)