import json

from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError

from users.models import User
from users.validation import phone_validate, password_validate


class SignUpViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('signup')

    def test_signup_with_valid_credentials(self):
        data = {
            'phone': '010-1234-5678',
            'password': 'Jisoo1234'
        }
        response = self.client.post(self.url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().phone, data['phone'])

    def test_signup_with_invalid_phone(self):
        data = {
            'phone': '010-1234',
            'password': 'Jisoo1234'
        }
        with self.assertRaises(ValidationError) as context:
            phone_validate(data['phone'])
        self.assertEqual(str(context.exception), "['INVALID_PHONE_NUMBER']")

    def test_signup_with_invalid_password(self):
        data = {
            'phone': '010-1234-5678',
            'password': 'wrong_password'
        }
        with self.assertRaises(ValidationError) as context:
            password_validate(data['password'])
        self.assertEqual(str(context.exception), "['INVALID_PASSWORD']")

    def test_signup_with_existing_phone(self):
        User.objects.create(phone='010-1234-5678', password='Jisoo1234')
        data = {
            'phone': '010-1234-5678',
            'password': 'Jisoo1234'
        }
        response = self.client.post(self.url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), 1)
