from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid
import os

class User(AbstractUser):
    USER_TYPES = (
        ('ops', 'Operations User'),
        ('client', 'Client User'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.user_type})"

def upload_to(instance, filename):
    return f'uploads/{instance.uploaded_by.username}/{filename}'

class UploadedFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to=upload_to)
    original_filename = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.BigIntegerField()
    file_type = models.CharField(max_length=10)
    
    def __str__(self):
        return f"{self.original_filename} by {self.uploaded_by.username}"

class DownloadToken(models.Model):
    token = models.CharField(max_length=100, unique=True)
    file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"Token for {self.file.original_filename}"
