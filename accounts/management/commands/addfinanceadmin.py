from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Add a user to the Finance Admin group by email.'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='User email to add to Finance Admin group')

    def handle(self, *args, **options):
        email = options['email']
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User with email {email} does not exist.'))
            return
        group, _ = Group.objects.get_or_create(name='Finance Admin')
        user.groups.add(group)
        user.save()
        self.stdout.write(self.style.SUCCESS(f'User {email} added to Finance Admin group.'))
