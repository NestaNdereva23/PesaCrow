
from .models import ProjectRequest, ContractTemplate, ContractSection, Contract
from django.utils import timezone
from django.contrib.auth.models import User
from profiles.models import UserProfile
from projects.models import Milestone
from decimal import Decimal


def create_contract_from_template(project_id):

    """generate a new contract with clauses from templates for a project"""
    project_request = ProjectRequest.objects.get(id=project_id)

    #create a contract
    contract = Contract.objects.create(project=project_request)

    #get all template sections and create sections
    templates = ContractTemplate.objects.all().order_by('id')
    print(ContractTemplate.objects.all().order_by('id').query)

    for index, template in enumerate(templates):
        #determine of certain section is editable or not
        editable = template.section_key in ['parties involved', 'payment_schedule', 'timeline', 'milestones', 'Scope of Work']

        #create section with content from template
        section = ContractSection.objects.create(
            contract=contract,
            template=template,
            title=template.name,
            content=template.content,
            editable=editable,
            order=index
        )
        print(f"Created section: {section.title} for contract {contract.id}")
    
    #populate dynamic content from project
    populate_contract_with_project_data(contract, project_request)
    return contract

def populate_contract_with_project_data(contract, project_request):
    #fill in contract sections with project specific data
    try:
        sender_user = User.objects.get(email=project_request.sender_email)
        sender_profile = UserProfile.objects.get(user=sender_user)
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        sender_user = None
        sender_profile = None

    try:
        receiver_user = User.objects.get(email=project_request.receiver_email)
        receiver_profile = UserProfile.objects.get(user=receiver_user)
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        receiver_user = None
        receiver_profile = None

    # Assign roles correctly
    if sender_profile and sender_profile.role_type == 'Client':
        client = sender_user
        client_profile = sender_profile
        developer = receiver_user
        developer_profile = receiver_profile
    else:
        developer = sender_user
        developer_profile = sender_profile
        client = receiver_user
        client_profile = receiver_profile

    try:
        parties_section = contract.sections.get(template__section_key='parties_involved')
        if parties_section:
            parties_content = parties_section.content

            if developer and developer_profile:

                #replave placeholders with actual data
                parties_content = parties_content.replace('[Your Company Name / Your Name]', developer.get_full_name())
                # parties_content = parties_content.replace('[Your Address]', developer.profile.address)
                parties_content = parties_content.replace('[Your Email]', developer.email)
                parties_content = parties_content.replace('[Your Phone Number]', developer_profile.phone_number)

            if client and client_profile:
                parties_content = parties_content.replace('[Client Name]', client.get_full_name())
                # parties_content = parties_content.replace('[Client Address]', client.profile.address)
                parties_content = parties_content.replace('[Client Email]', client.email)
                parties_content = parties_content.replace('[Client Phone Number]', client_profile.phone_number)

            parties_section.content = parties_content
            parties_section.save()
        else:
            print("no parties section")

    except ContractSection.DoesNotExist:
        pass

    # Update project details section
    try:
        project_section = contract.sections.get(template__section_key='project_details')
        project_content = project_section.content
        
        # Replace project details
        project_content = project_content.replace('[Provide a more detailed description of the project here.]', project_request.project_description)
        
        
        project_content = project_content.replace('[Project Start Date]', project_request.created_at.strftime('%Y-%m-%d'))
        project_content = project_content.replace('[Projected End Date]', '')
        
        # Get milestones for this project request
        # from projects.models import Milestone 
        milestones = Milestone.objects.filter(project=project_request)
        
        milestones_text = ""
        for index, milestone in enumerate(milestones, 1):
            milestones_text += f"● Milestone {index}: {milestone.title} - {milestone.estimated_completion.strftime('%Y-%m-%d')}\n"
        
        if not milestones_text:
            milestones_text = "● Milestones to be determined"
            
        project_content = project_content.replace('● Milestone 1: [Description & Expected Completion Date]\n● Milestone 2: [Description & Expected Completion Date]\n● ...', milestones_text)
        
        
        if project_request.budget:
            budget_text = f"\n● Budget: ${project_request.budget}"
            project_content += budget_text
            
        
        if project_request.requirements:
            requirements_text = f"\n● Requirements: {project_request.requirements}"
            project_content += requirements_text
        
        project_section.content = project_content
        project_section.save()
    except ContractSection.DoesNotExist:
        pass
    
    # Update payment section 
    try:
        payment_section = contract.sections.get(template__section_key='budget_and_payment')
        payment_content = payment_section.content
        
        # Replace payment details
        if project_request.budget:
            payment_content = payment_content.replace('[Specify Amount]', f"${project_request.budget}")
            
            # Calculate milestone payments if milestones exist
            milestones = Milestone.objects.filter(project=project_request)
            if milestones.exists():
                milestone_count = milestones.count()
                upfront_percentage = 25  
                final_percentage = 25   
                milestone_percentage = (100 - upfront_percentage - final_percentage) / milestone_count
                
                # Update the payment schedule
                payment_content = payment_content.replace('[Specify Percentage or Amount] payable upon signing', 
                                                         f"{upfront_percentage}% (Kshs. {project_request.budget * upfront_percentage/100:.2f}) payable upon signing")
                
                milestone_payment_text = ""
                for index, milestone in enumerate(milestones, 1):
                    milestone_payment_text += f"■ After Milestone {index} completion: {milestone_percentage}% (Kshs. {project_request.budget * Decimal(milestone_percentage) / Decimal(100):.2f})\n"
                
                payment_content = payment_content.replace('■ After Milestone 1 completion: [Specify Percentage or Amount]\n■ After Milestone 2 completion: [Specify Percentage or Amount]\n■ ...', 
                                                         milestone_payment_text)
                
                payment_content = payment_content.replace('[Specify Percentage or Amount] payable upon project completion',
                                                         f"{final_percentage}% (Kshs. {project_request.budget * final_percentage/100:.2f}) payable upon project completion")
        
        payment_section.content = payment_content
        payment_section.save()
    except ContractSection.DoesNotExist:
        pass