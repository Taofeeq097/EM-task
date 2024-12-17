import os
from django.core.management.base import BaseCommand
from accounts.models import Role, User
from base.constants import EmployeeRoles


class Command(BaseCommand):
    help = 'Seed CEO User account, double as superuser'

    def handle(self, *args, **kwargs):
        print(Role.active_objects.all())
        print(EmployeeRoles.CEO)
        ceo_role, _ = Role.active_objects.get_or_create(name=EmployeeRoles.CEO)

        if not User.objects.filter(role__name=EmployeeRoles.CEO).exists():
            data = {
                'first_name': os.environ.get('CEO_FIRST_NAME', 'ceo first name'),
                'last_name': os.environ.get('CEO_LAST_NAME', 'ceo last name'),
                'email': os.environ.get('CEO_EMAIL', 'ceoadmin@email.com'),
                'role_id': ceo_role.id,
            }
            ceo=User.objects.create_user(**data)
            ceo.set_password(os.environ.get('CEO_USER_PASSWORD', 'Password@1'))
            ceo.is_superuser = True
            ceo.is_staff = True
            ceo.save()

        self.stdout.write(self.style.SUCCESS('Successfully created CEO user'))

