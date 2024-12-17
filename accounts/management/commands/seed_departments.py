from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from accounts.models import Department
from base.constants import EmployeeDepartments


class Command(BaseCommand):
    help = 'Seeds the Role model with predefined roles'

    def handle(self, *args, **kwargs):
        roles = [
            Department(name=role, description=f"{role} department in the organization")
            for role in EmployeeDepartments.values
        ]
        try:
            Department.active_objects.bulk_create(roles, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS("Department seeded successfully."))
        except IntegrityError as e:
            self.stderr.write(self.style.ERROR(f"Error seeding Departments: {e}"))
