from cryptography.fernet import Fernet
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
import secrets
import base64
import hashlib

def generate_encryption_key():
    """Generate a key for encryption"""
    return Fernet.generate_key()

def encrypt_data(data, key=None):
    """Encrypt data using Fernet encryption"""
    if key is None:
        key = settings.SECRET_KEY.encode()[:32]
        key = base64.urlsafe_b64encode(hashlib.sha256(key).digest())
    
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data.decode()

def decrypt_data(encrypted_data, key=None):
    """Decrypt data using Fernet encryption"""
    if key is None:
        key = settings.SECRET_KEY.encode()[:32]
        key = base64.urlsafe_b64encode(hashlib.sha256(key).digest())
    
    f = Fernet(key)
    try:
        decrypted_data = f.decrypt(encrypted_data.encode())
        return decrypted_data.decode()
    except:
        return None

def generate_secure_token():
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)

def send_verification_email(user, verification_url):
    """Send email verification"""
    subject = 'Verify your email address'
    message = f'''
    Hi {user.first_name or user.username},
    
    Please click the link below to verify your email address:
    {verification_url}
    
    This link will expire in 24 hours.
    
    Best regards,
    File Sharing Team
    '''
    
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )
