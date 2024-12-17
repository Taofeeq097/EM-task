from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Run all project required seed commands'

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.NOTICE('App installation Starting...'))
            call_command('seed_roles')
            call_command('seed_departments')
            call_command('seed_ceo_user')
            call_command('makemigrations')
            call_command('migrate')
            self.stdout.write(self.style.SUCCESS('App installation completed successfully.'))
        except CommandError as e:
            self.stderr.write(self.style.ERROR(f'Error during app installation: {str(e)}'))