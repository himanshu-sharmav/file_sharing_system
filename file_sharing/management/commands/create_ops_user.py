from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create an Operations user for file uploads'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='opsuser', help='Username for ops user')
        parser.add_argument('--email', type=str, default='ops@example.com', help='Email for ops user')
        parser.add_argument('--password', type=str, default='opspass123', help='Password for ops user')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'Operations user "{username}" already exists'))
            return

        ops_user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            user_type='ops'
        )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created Operations user: {username}'))
        self.stdout.write(f'Username: {username}')
        self.stdout.write(f'Password: {password}')
