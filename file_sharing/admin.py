from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UploadedFile, DownloadToken

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'user_type', 'is_email_verified', 'is_active']
    list_filter = ['user_type', 'is_email_verified', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('user_type', 'is_email_verified', 'email_verification_token')}),
    )

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'uploaded_by', 'file_type', 'file_size', 'uploaded_at']
    list_filter = ['file_type', 'uploaded_at']
    search_fields = ['original_filename', 'uploaded_by__username']

@admin.register(DownloadToken)
class DownloadTokenAdmin(admin.ModelAdmin):
    list_display = ['file', 'user', 'created_at', 'expires_at', 'is_used']
    list_filter = ['is_used', 'created_at']
