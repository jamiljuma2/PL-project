from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from accounts.models import User

class Command(BaseCommand):
    help = 'Create initial user groups and assign permissions.'

    def handle(self, *args, **options):
        # Define groups
        groups = [
            ('Admin', []),
            ('Writer', []),
            ('Student', []),
        ]

        # Create groups if they don't exist
        for group_name, perms in groups:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created group: {group_name}'))
            else:
                self.stdout.write(f'Group already exists: {group_name}')

        # Example: Assign all permissions to Admin
        admin_group = Group.objects.get(name='Admin')
        admin_perms = Permission.objects.all()
        admin_group.permissions.set(admin_perms)
        self.stdout.write(self.style.SUCCESS('Assigned all permissions to Admin group.'))

        self.stdout.write(self.style.SUCCESS('Groups and permissions setup complete.'))
