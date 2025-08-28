from django.test import TestCase
from django.contrib.auth.models import User
from .models import ProjectRequest, Milestone

class ProjectModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='password')
        self.project = ProjectRequest.objects.create(
            user=self.user,
            sender_email='testuser@example.com',
            receiver_email='client@example.com',
            title='Test Project',
            project_description='This is a test project.',
            budget=1000.00,
            requirements='Some requirements.'
        )

    def test_project_request_creation(self):
        self.assertEqual(self.project.title, 'Test Project')
        self.assertEqual(self.project.status, 'Pending')
        self.assertEqual(self.project.user.username, 'testuser')

    def test_milestone_creation(self):
        milestone = Milestone.objects.create(
            project=self.project,
            title='Test Milestone',
            description='This is a test milestone.',
            deliverables='Some deliverables.',
            payment_amount=500.00,
            estimated_completion='2025-12-31',
            order_number=1
        )
        self.assertEqual(milestone.title, 'Test Milestone')
        self.assertEqual(milestone.project, self.project)
        self.assertEqual(self.project.project_milestones.count(), 1)