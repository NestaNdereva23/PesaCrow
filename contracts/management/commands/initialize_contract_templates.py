from django.core.management.base import BaseCommand
from contracts.models import ContractTemplate


class Command(BaseCommand):
    help = 'Initialize contract templates with sections from the boilerplate'

    def handle(self, *args, **kwargs):
        templates = [
            {
                'name': 'Parties Involved',
                'section_key': 'parties_involved',
                'content': """● Developer:
● Name/Company: [Your Company Name / Your Name]
● Address: [Your Address]
● Email: [Your Email]
● Phone: [Your Phone Number]
● Client:
● Name/Company: [Client Name]
● Address: [Client Address]
● Email: [Client Email]
● Phone: [Client Phone Number]"""
            },
            {
                'name': 'Project Details',
                'section_key': 'project_details',
                'content': """● Description:
● A brief overview of the web development project's primary goals, features, and
deliverables. [Provide a more detailed description of the project here.]
● Timeline:
● Start Date: [Project Start Date]
● End Date: [Projected End Date]
● Milestones:
● Milestone 1: [Description & Expected Completion Date]
● Milestone 2: [Description & Expected Completion Date]
● ...
● Note: Milestones serve as major checkpoints or stages in the project, ensuring
that both parties are aligned on expectations and deliverables."""
            },
            {
                'name': 'Technical Specifications',
                'section_key': 'technical_specifications',
                'content': """● Technical Overview:
● A brief summary of the technical aspects, frameworks, and tools that will be used
for the project. [Specify the technologies, platforms, and software that will be
employed.]
● System Design & Functionality:
● Frontend: [Describe the front-end components, user interfaces, design principles,
etc.]
● Backend: [Describe server-side components, databases, data flow, etc.]
● APIs and Integrations: [Detail any third-party integrations or APIs that will be
used.]
● Security Measures:
● Outline of measures taken to ensure the website/software's security. [Detail any
encryption, authentication, or other security protocols.]"""
            },
            {
                'name': 'Scope of Work',
                'section_key': 'scope_of_work',
                'content': """● Overall Tasks:
● A general overview of tasks, activities, and responsibilities that the Developer will
undertake during the project's lifecycle.
● Task Breakdown:
● Front-end Development: [Specific tasks related to the user interface, graphics,
responsiveness, etc.]
● Back-end Development: [Specific tasks related to server interactions, database
operations, data management, etc.]
● CMS Integration: [If applicable, tasks related to content management system
implementation.]
● SEO Optimization: [Tasks ensuring the website is search-engine friendly.]
● Quality Assurance: [Tasks related to testing, bug fixing, and ensuring the product
meets the quality standards.]
● Client Responsibilities:
● Any tasks, materials, feedback, or approvals that the Client must provide to aid
the development process. This might include content, branding materials, access
to servers, etc."""
            },
            {
                'name': 'Budget and Payment',
                'section_key': 'budget_and_payment',
                'content': """● Total Project Cost:
○ The agreed total amount for the project is [Specify Amount].
● Payment Schedule:
○ Upfront/Deposit: [Specify Percentage or Amount] payable upon signing the
agreement.
○ Milestone Payments:
■ After Milestone 1 completion: [Specify Percentage or Amount]
■ After Milestone 2 completion: [Specify Percentage or Amount]
■ ...
○ Final Payment: [Specify Percentage or Amount] payable upon project completion
and acceptance.
● Accepted Payment Methods:
○ [Bank Transfer, PayPal, Credit Card, etc.]
● Late Payment Policy:
○ Payments overdue by [Specify Number] days will incur a [Specify Percentage]
late fee. Further delays may result in a halt in project work until outstanding
balances are settled."""
            },
            # Add more sections as needed from your template document
            {
                'name': 'Intellectual Property and Copyright',
                'section_key': 'intellectual_property',
                'content': """● Ownership Rights:
○ Upon full payment and completion of the project, the intellectual property rights of
the developed website/software will be transferred to the Client. Until then, all
rights remain with the Developer.
● Usage Rights:
○ Maintenance: The Client has the right to maintain, update, and modify the
website or software after the completion of the project. If not stated otherwise,
maintenance post-launch is the responsibility of the Client.
○ Marketing: The Developer reserves the right to showcase the completed project
in portfolios, marketing materials, and case studies unless otherwise specified by
the Client.
● Third-party Materials:
○ Any third-party materials used in the project (e.g., stock photos, plugins,
software) that have their licensing terms will remain under those terms and may
not transfer to the Client upon project completion."""
            },
            {
                'name':'Client Responsibilities',
                'section_key':'client_responsibilities',
                'content':"""Client Responsibilities:
● Provision of Materials:
    ○ The Client agrees to provide all necessary materials (such as content, logos,
    branding guidelines, and other relevant documents) in a timely manner to aid the
    development process
● Feedback and Approvals:
    ○ The Client commits to providing feedback, revisions, and approvals within
[Specify Number of Days, e.g., "5 business days"] of receiving requests from the
Developer. Delays may result in project timeline extensions.
● Access:
    ○ The Client will grant the Developer access to necessary platforms, servers, or
software when required for the completion of tasks.
●  Point of Contact:    
    ○ The Client will designate a primary point of contact who will communicate with
the Developer, ensuring consistency and clarity in feedback and decisions. """
            },
        ]

        created_count = 0
        updated_count = 0

        for template_data in templates:
            template, created = ContractTemplate.objects.update_or_create(
                section_key=template_data['section_key'],
                defaults={
                    'name': template_data['name'],
                    'content': template_data['content']
                }
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Successfully processed {len(templates)} contract template sections: '
            f'{created_count} created, {updated_count} updated'
        ))