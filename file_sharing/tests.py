from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import UploadedFile, DownloadToken

User = get_user_model()

class UserAuthTestCase(APITestCase):
    def setUp(self):
        self.ops_user = User.objects.create_user(
            username='opsuser',
            email='ops@test.com',
            password='testpass123',
            user_type='ops'
        )
        
    def test_client_signup(self):
        """Test client user registration"""
        data = {
            'username': 'clientuser',
            'email': 'client@test.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123',
            'first_name': 'Client',
            'last_name': 'User'
        }
        response = self.client.post(reverse('client_signup'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='clientuser').exists())
    
    def test_user_login(self):
        """Test user login"""
        data = {
            'username': 'opsuser',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('user_login'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

class FileOperationsTestCase(APITestCase):
    def setUp(self):
        self.ops_user = User.objects.create_user(
            username='opsuser',
            email='ops@test.com',
            password='testpass123',
            user_type='ops'
        )
        
        self.client_user = User.objects.create_user(
            username='clientuser',
            email='client@test.com',
            password='testpass123',
            user_type='client',
            is_email_verified=True
        )
        
    def test_file_upload_by_ops_user(self):
        """Test file upload by operations user"""
        self.client.force_authenticate(user=self.ops_user)
        
        # Create a test file
        test_file = SimpleUploadedFile(
            "test.docx",
            b"file_content",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
        data = {'file': test_file}
        response = self.client.post(reverse('upload_file'), data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_file_upload_by_client_user_forbidden(self):
        """Test that client users cannot upload files"""
        self.client.force_authenticate(user=self.client_user)
        
        test_file = SimpleUploadedFile("test.docx", b"file_content")
        data = {'file': test_file}
        response = self.client.post(reverse('upload_file'), data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_list_files_by_client_user(self):
        """Test file listing by client user"""
        self.client.force_authenticate(user=self.client_user)
        response = self.client.get(reverse('list_files'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('files', response.data)
