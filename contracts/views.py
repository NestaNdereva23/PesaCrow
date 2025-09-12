from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponse
from django.forms import modelformset_factory
from django.urls import reverse
from .models import ProjectRequest, Contract, ContractSection
from .services import create_contract_from_template
from .forms import ContractSectionForm
from django.core.management import call_command
from projects.models import Milestone
from django.template.loader import get_template
from xhtml2pdf import pisa

def ensure_contract_templates_exist():
    call_command('initialize_contract_templates')

@login_required
def contract(request):
    user=request.user

    if user.userprofile.role_type == 'Client':
        contracts = Contract.objects.filter(project__sender_email=request.user.email, project__verified=True)
        context = {"contracts": contracts}
        return render(request, "contracts/contracts.html", context)
    elif user.userprofile.role_type == 'Developer':
        contracts = Contract.objects.filter(project__receiver_email=request.user.email, project__verified=True)
        context = {"contracts": contracts}
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

    return redirect('contracts:edit_contract', contract_id=contract.id)

@login_required
def edit_contract(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    project = contract.project

    if request.user.email != project.sender_email and request.user.email != project.receiver_email:
        return HttpResponseForbidden("You dont have access to this contract")

    if request.method == 'POST':
        section_id = request.POST.get('section_id')
        section = get_object_or_404(ContractSection, id=section_id, contract=contract, editable=True)
        
        form = ContractSectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, f"Section '{section.title}' updated successfully.")
        else:
            messages.error(request, "There was an error updating the section.")
        
        return redirect('contracts:edit_contract', contract_id=contract.id)

    all_sections = contract.sections.all().order_by('order')
    sections_with_forms = []
    for section in all_sections:
        form = None
        if section.editable:
            form = ContractSectionForm(instance=section)
        sections_with_forms.append({'section': section, 'form': form})

    context = {
        'contract': contract,
        'project': project,
        'sections_with_forms': sections_with_forms
    }

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

@login_required
def view_contract(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    project = contract.project

    if request.user.email != project.sender_email and request.user.email != project.receiver_email:
        return HttpResponseForbidden("You dont have access to this contract")

    context = {'contract': contract}
    return render(request, 'contracts/view_contract.html', context)

@login_required
def download_contract_pdf(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    project = contract.project

    if request.user.email != project.sender_email and request.user.email != project.receiver_email:
        return HttpResponseForbidden("You dont have access to this contract")

    if not contract.signed_by_client or not contract.signed_by_developer:
        return HttpResponseForbidden("Contract is not finalized yet")

    template_path = 'contracts/contract_pdf_template.html'
    sections = contract.sections.all().order_by('order')
    context = {'contract': contract, 'sections': sections}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="contract_{contract.id}.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(
       html, dest=response)

    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response