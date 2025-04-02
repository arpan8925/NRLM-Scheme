from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Manager

User = get_user_model()

class Command(BaseCommand):
    help = 'Create manager profiles for users that dont have one'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        created = 0
        
        for user in users:
            # Skip if user already has a manager profile
            if hasattr(user, 'dashboard_manager') or hasattr(user, 'account_manager'):
                continue
                
            Manager.objects.create(
                user=user,
                department='Default Department',
                phone_number='0000000000'
            )
            created += 1
            
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created} manager profiles')
        ) 