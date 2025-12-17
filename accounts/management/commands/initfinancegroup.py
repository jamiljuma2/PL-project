from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Create Finance Admin group for payment approval.'

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name='Finance Admin')
        if created:
            self.stdout.write(self.style.SUCCESS('Finance Admin group created.'))
        else:
            self.stdout.write('Finance Admin group already exists.')
