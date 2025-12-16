
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from .models import User, PasswordReset
import datetime

class PasswordResetConfirmTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='testuser', email='test@example.com', password='oldpassword')
		self.token = 'valid-token-123'
		self.reset_obj = PasswordReset.objects.create(user=self.user, token=self.token)
		self.client = APIClient()
		self.url = reverse('auth-password-reset-confirm')

	def test_password_reset_confirm_success(self):
		response = self.client.post(self.url, {'token': self.token, 'new_password': 'Newpass123!'}, format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertIn('detail', response.data)
		self.user.refresh_from_db()
		self.assertTrue(self.user.check_password('Newpass123!'))
		self.reset_obj.refresh_from_db()
		self.assertTrue(self.reset_obj.is_used)

	def test_password_reset_confirm_invalid_token(self):
		response = self.client.post(self.url, {'token': 'wrong-token', 'new_password': 'Newpass123!'}, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn('token', response.data)

	def test_password_reset_confirm_used_token(self):
		self.reset_obj.is_used = True
		self.reset_obj.save()
		response = self.client.post(self.url, {'token': self.token, 'new_password': 'Newpass123!'}, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn('token', response.data)

	def test_password_reset_confirm_expired_token(self):
		self.reset_obj.created_at = timezone.now() - datetime.timedelta(hours=2)
		self.reset_obj.save()
		response = self.client.post(self.url, {'token': self.token, 'new_password': 'Newpass123!'}, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn('token', response.data)
