```markdown
# Secure File Sharing System

A Django REST API-based secure file sharing system that allows Operations users to upload files and Client users to download them through encrypted URLs.

## 🚀 Features

- **User Authentication**: Separate login for Operations and Client users
- **Email Verification**: Client users must verify their email before accessing the system
- **Secure File Upload**: Only Operations users can upload .pptx, .docx, and .xlsx files
- **Encrypted Download URLs**: Secure, time-limited download links for Client users
- **File Management**: List all uploaded files with metadata
- **Token-based Authentication**: JWT-like token authentication for API security

## 🛠️ Technology Stack

- **Backend**: Django 4.x, Django REST Framework
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Authentication**: Token-based authentication
- **File Storage**: Local file system (configurable for cloud storage)
- **Email**: SMTP support for email verification

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

## ⚡ Quick Start

### 1. Clone the Repository

```
git clone 
cd file_sharing_system
```

### 2. Create Virtual Environment

```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```
pip install -r requirements.txt
```

### 4. Environment Setup

Create a `.env` file in the project root:

```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 5. Database Setup

```
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser

```
python manage.py createsuperuser
```

### 7. Create Operations User

```
python manage.py shell
```

In the Django shell:
```
from django.contrib.auth import get_user_model
User = get_user_model()

# Create Operations user
ops_user = User.objects.create_user(
    username='opsuser',
    email='ops@example.com',
    password='opspass123',
    user_type='ops'
)
print("Operations user created successfully!")
exit()
```

### 8. Run the Server

```
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api/
```

### Authentication
Protected endpoints require a token in the Authorization header:
```
Authorization: Token 
```

### Endpoints

#### 🔐 Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/signup/` | Client user registration | No |
| GET | `/verify-email/?token=` | Email verification | No |
| POST | `/login/` | User login (ops/client) | No |

#### 📁 File Operations

| Method | Endpoint | Description | Auth Required | User Type |
|--------|----------|-------------|---------------|-----------|
| POST | `/upload/` | Upload file | Yes | Operations |
| GET | `/files/` | List all files | Yes | Client |
| GET | `/download-file//` | Generate download link | Yes | Client |
| GET | `/secure-download//` | Download file | No | Token-based |

### Request/Response Examples

#### Client Registration
```
POST /api/signup/
Content-Type: application/json

{
    "username": "clientuser",
    "email": "client@example.com",
    "password": "testpass123",
    "confirm_password": "testpass123",
    "first_name": "Client",
    "last_name": "User"
}
```

#### User Login
```
POST /api/login/
Content-Type: application/json

{
    "username": "clientuser",
    "password": "testpass123"
}
```

Response:
```
{
    "token": "your_auth_token_here",
    "user_type": "client",
    "username": "clientuser",
    "message": "Login successful"
}
```

#### File Upload (Operations User)
```
POST /api/upload/
Authorization: Token 
Content-Type: multipart/form-data

file: 
```

#### Generate Download Link (Client User)
```
GET /api/download-file//
Authorization: Token 
```

Response:
```
{
    "download_link": "http://localhost:8000/api/secure-download//",
    "message": "success",
    "expires_at": "2025-07-02T02:32:00Z"
}
```

## 🧪 Testing

### Run Unit Tests
```
python manage.py test
```

### Test with Postman
1. Import the provided Postman collection
2. Set up environment variables:
   - `base_url`: `http://localhost:8000/api`
   - `client_token`: (obtained from login)
   - `ops_token`: (obtained from login)
3. Run the requests in sequence

### Manual Testing Flow
1. Register a client user → Verify email → Login
2. Login as operations user
3. Upload a file (ops user)
4. List files (client user)
5. Generate download link (client user)
6. Download file using the secure URL

## 🔒 Security Features

- **Token-based Authentication**: Secure API access
- **Email Verification**: Prevents unauthorized registrations
- **File Type Validation**: Only allows .pptx, .docx, .xlsx files
- **Encrypted Download URLs**: Time-limited, single-use download tokens
- **User Role Separation**: Clear separation between Operations and Client users
- **File Size Limits**: 10MB maximum file size

## 📁 Project Structure

```
file_sharing_system/
├── file_sharing_system/
│   ├── settings.py          # Django settings
│   ├── urls.py             # Main URL configuration
│   └── wsgi.py             # WSGI configuration
├── file_sharing/
│   ├── models.py           # Database models
│   ├── views.py            # API views
│   ├── serializers.py      # DRF serializers
│   ├── urls.py             # App URL configuration
│   ├── utils.py            # Utility functions
│   ├── admin.py            # Admin configuration
│   └── tests.py            # Unit tests
├── media/                  # Uploaded files
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## 🚀 Deployment

### Production Checklist

1. **Environment Variables**
   ```
   DEBUG=False
   ALLOWED_HOSTS=yourdomain.com
   SECRET_KEY=your-production-secret-key
   ```

2. **Database**
   - Use PostgreSQL for production
   - Configure database credentials in `.env`

3. **Static Files**
   ```
   python manage.py collectstatic
   ```

4. **Security**
   - Enable HTTPS
   - Configure CORS settings
   - Set up proper firewall rules

### Deployment Options

- **Heroku**: Easy deployment with PostgreSQL addon
- **AWS EC2**: Full control with RDS for database
- **DigitalOcean**: App Platform or Droplets
- **Docker**: Containerized deployment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support or questions, please contact:
- Email: your-email@example.com
- GitHub Issues: [Create an issue](https://github.com/himanshu-sharmav/file-sharing-system/issues)

## 🙏 Acknowledgments

- Django REST Framework documentation
- Django community for excellent resources
- Contributors and testers

---

**Note**: This project was created as part of a technical assessment for a Back-End Intern position.
```
