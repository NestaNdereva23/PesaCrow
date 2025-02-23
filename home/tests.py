from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from home.forms import RegistrationForm

# Create your tests here.
class RegistrationTests(TestCase):
    def setUp(self):
        User.objects.create_user(
            username='test',
            email='test@gmail.com',
            password='test123',
            # confirm_password='test123'
        )

    def test_email_is_unique(self):

        form_data = {

            'username': 'test2',
            'email': 'test2@gmail.com',
            'password1': 'test123P123msn3im2dn',
            'password2': 'test123P123msn3im2dn',
        }
        form = RegistrationForm(data=form_data)

        #check for duplicate email
        self.assertTrue(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertEqual(form.errors['email'], ['This email is already in use.'])

    def test_user_registration(self):
        form_data = {
            'username': 'test2',
            'email': 'test2@gmail.com',
            'password1': 'test123P123msn3im2dn',
            'password2': 'test123P123msn3im2dn',

        }
        response = self.client.post(reverse('registration'), data=form_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))