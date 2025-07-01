from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.client_signup, name='client_signup'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('login/', views.user_login, name='user_login'),
    path('upload/', views.upload_file, name='upload_file'),
    path('files/', views.list_files, name='list_files'),
    path('download-file/<uuid:file_id>/', views.download_file, name='download_file'),
    path('secure-download/<str:token>/', views.secure_download, name='secure_download'),
]
