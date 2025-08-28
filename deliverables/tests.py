from django.test import TestCase
from django.contrib.auth.models import User
from projects.models import ProjectRequest, Milestone
from .models import Deliverable, DeliverableReview

class DeliverableModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='password')
        self.client = User.objects.create_user(username='client', email='client@example.com', password='password')
        self.project = ProjectRequest.objects.create(
            user=self.user,
            sender_email='testuser@example.com',
            receiver_email='client@example.com',
            title='Test Project',
            project_description='This is a test project.',
            budget=1000.00,
            requirements='Some requirements.'
        )
        self.milestone = Milestone.objects.create(
            project=self.project,
            title='Test Milestone',
            description='This is a test milestone.',
            deliverables='Some deliverables.',
            payment_amount=500.00,
            estimated_completion='2025-12-31',
            order_number=1
        )
        self.deliverable = Deliverable.objects.create(
            milestone=self.milestone,
            developer=self.user,
            title='Test Deliverable',
            description='This is a test deliverable.'
        )

    def test_deliverable_creation(self):
        self.assertEqual(self.deliverable.title, 'Test Deliverable')
        self.assertEqual(self.deliverable.status, 'pending')
        self.assertEqual(self.deliverable.milestone, self.milestone)
        self.assertEqual(self.milestone.milestone_deliverables.count(), 1)

    def test_deliverable_review_creation(self):
        review = DeliverableReview.objects.create(
            deliverable=self.deliverable,
            reviewer=self.client,
            decision='approved',
            comments='Looks good!'
        )
        self.assertEqual(review.decision, 'approved')
        self.assertEqual(review.deliverable, self.deliverable)
        self.assertEqual(self.deliverable.reviews.count(), 1)
