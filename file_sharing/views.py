from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
import os
import mimetypes

from .models import User, UploadedFile, DownloadToken
from .serializers import (
    UserRegistrationSerializer, 
    LoginSerializer, 
    FileUploadSerializer,
    UploadedFileSerializer
)
from .utils import generate_secure_token, encrypt_data, decrypt_data, send_verification_email

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def client_signup(request):
    """Client user registration"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Generate verification token
        verification_token = generate_secure_token()
        user.email_verification_token = verification_token
        user.save()
        
        # Create encrypted verification URL
        verification_url = f"{request.build_absolute_uri('/api/verify-email/')}?token={verification_token}"
        
        # Send verification email
        try:
            send_verification_email(user, verification_url)
        except Exception as e:
            print(f"Email sending failed: {e}")
        
        return Response({
            'message': 'User registered successfully. Please check your email for verification.',
            'verification_url': verification_url  # For testing purposes
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def verify_email(request):
    """Verify user email"""
    token = request.GET.get('token')
    if not token:
        return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email_verification_token=token)
        user.is_email_verified = True
        user.email_verification_token = None
        user.save()
        
        return Response({'message': 'Email verified successfully'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def user_login(request):
    """User login for both ops and client users"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Check if client user has verified email
        if user.user_type == 'client' and not user.is_email_verified:
            return Response({
                'error': 'Please verify your email before logging in'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_type': user.user_type,
            'username': user.username,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_file(request):
    """File upload for ops users only"""
    if request.user.user_type != 'ops':
        return Response({
            'error': 'Only Operations users can upload files'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = FileUploadSerializer(data=request.data)
    if serializer.is_valid():
        uploaded_file = serializer.save(
            uploaded_by=request.user,
            original_filename=request.FILES['file'].name,
            file_size=request.FILES['file'].size,
            file_type=request.FILES['file'].name.split('.')[-1].lower()
        )
        
        return Response({
            'message': 'File uploaded successfully',
            'file_id': uploaded_file.id,
            'filename': uploaded_file.original_filename
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_files(request):
    """List all uploaded files for client users with pagination and filtering"""
    if request.user.user_type != 'client':
        return Response({
            'error': 'Only Client users can list files'
        }, status=status.HTTP_403_FORBIDDEN)
    
    files = UploadedFile.objects.all().order_by('-uploaded_at')
    
    # Filter by file type if provided
    file_type = request.query_params.get('file_type', None)
    if file_type:
        files = files.filter(file_type=file_type)
    
    # Search by filename
    search = request.query_params.get('search', None)
    if search:
        files = files.filter(original_filename__icontains=search)
    
    serializer = UploadedFileSerializer(files, many=True)
    
    return Response({
        'files': serializer.data,
        'count': files.count()
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_file(request, file_id):
    """Generate secure download link for client users"""
    if request.user.user_type != 'client':
        return Response({
            'error': 'Only Client users can download files'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        uploaded_file = UploadedFile.objects.get(id=file_id)
    except UploadedFile.DoesNotExist:
        return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Generate secure download token
    download_token = generate_secure_token()
    expires_at = timezone.now() + timedelta(hours=1)  # Token expires in 1 hour
    
    DownloadToken.objects.create(
        token=download_token,
        file=uploaded_file,
        user=request.user,
        expires_at=expires_at
    )
    
    download_url = request.build_absolute_uri(f'/api/secure-download/{download_token}/')
    
    return Response({
        'download_link': download_url,
        'message': 'success',
        'expires_at': expires_at
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def secure_download(request, token):
    """Secure file download endpoint"""
    try:
        download_token = DownloadToken.objects.get(token=token)
        
        # Check if token is expired
        if download_token.is_expired():
            return Response({'error': 'Download link has expired'}, status=status.HTTP_410_GONE)
        
        # Check if token is already used
        if download_token.is_used:
            return Response({'error': 'Download link has already been used'}, status=status.HTTP_410_GONE)
        
        # Mark token as used
        download_token.is_used = True
        download_token.save()
        
        # Get the file
        uploaded_file = download_token.file
        
        if not os.path.exists(uploaded_file.file.path):
            return Response({'error': 'File not found on server'}, status=status.HTTP_404_NOT_FOUND)
        
        # Serve the file
        with open(uploaded_file.file.path, 'rb') as f:
            file_data = f.read()
        
        content_type, _ = mimetypes.guess_type(uploaded_file.file.path)
        response = HttpResponse(file_data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{uploaded_file.original_filename}"'
        
        return response
        
    except DownloadToken.DoesNotExist:
        return Response({'error': 'Invalid download link'}, status=status.HTTP_404_NOT_FOUND)
