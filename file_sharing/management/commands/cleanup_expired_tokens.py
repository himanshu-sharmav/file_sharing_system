from django.core.management.base import BaseCommand
from django.utils import timezone
from file_sharing.models import DownloadToken

class Command(BaseCommand):
    help = 'Clean up expired download tokens'

    def handle(self, *args, **options):
        expired_tokens = DownloadToken.objects.filter(expires_at__lt=timezone.now())
        count = expired_tokens.count()
        expired_tokens.delete()
        
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} expired download tokens'))
