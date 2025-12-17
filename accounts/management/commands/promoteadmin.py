from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Promote a user to admin and superuser by email.'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='User email to promote')

    def handle(self, *args, **options):
        email = options['email']
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User with email {email} does not exist.'))
            return
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        user.groups.add(admin_group)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        self.stdout.write(self.style.SUCCESS(f'User {email} promoted to admin and superuser.'))
