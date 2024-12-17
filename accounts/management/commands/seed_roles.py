from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from accounts.models import Role
from base.constants import EmployeeRoles


class Command(BaseCommand):
    help = 'Seeds the Role model with predefined roles'

    def handle(self, *args, **kwargs):
        roles = [
            Role(name=role, description=f"{role} role in the organization")
            for role in EmployeeRoles.values
        ]


        try:
            Role.active_objects.bulk_create(roles, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS("Roles seeded successfully."))
        except IntegrityError as e:
            self.stderr.write(self.style.ERROR(f"Error seeding roles: {e}"))
