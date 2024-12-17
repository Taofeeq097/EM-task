from django.db.models import Prefetch
from rest_framework.exceptions import ValidationError

from accounts.models import User, Role, Department
from base.constants import EmployeeRoles


class AccountService:

    @classmethod
    def get_user(cls, user_id):
        try:
            return User.active_objects.get(pk=user_id)
        except User.DoesNotExist:
            raise ValidationError(f'User with ID {user_id} does not exist')

    @classmethod
    def _get_role(cls, role_id):
        try:
            return Role.active_objects.get(id=role_id)
        except Role.DoesNotExist:
            raise ValidationError(f'Role with ID {role_id} does not exist')

    @classmethod
    def _get_department(cls, department_id):
        try:
            return Department.active_objects.get(pk=department_id)
        except Department.DoesNotExist:
            raise ValidationError(f'Department with ID {department_id} does not exist')

    @classmethod
    def _validate_duplicate_ceo_employee(self, role_id, user_id=None):
        role = self._get_role(role_id)

        if role.name == EmployeeRoles.CEO:
            duplicate_ceo = User.active_objects.filter(role__name=EmployeeRoles.CEO)
            if user_id:
                duplicate_ceo = duplicate_ceo.exclude(pk=user_id)

            if duplicate_ceo.exists():
                raise ValidationError({"Role": "An active account with ceo role already exists"})


    @classmethod
    def _validate_unique_email(self, email, user_id=None):
        duplicate_emails = User.active_objects.filter(email=email)
        if user_id:
            duplicate_emails = duplicate_emails.exclude(pk=user_id)

        if duplicate_emails.exists():
            raise ValidationError({"email": "An active account with this email already exists"})

    @classmethod
    def validate_selected_supervisor(cls, supervisor_id, role_id):
        role = cls._get_role(role_id)
        supervisor = cls.get_user(supervisor_id)
        supervisor_allowed_roles = {
            EmployeeRoles.EMPLOYEE: [EmployeeRoles.MANAGER, EmployeeRoles.DIRECTOR, EmployeeRoles.CEO],
            EmployeeRoles.MANAGER: [EmployeeRoles.DIRECTOR, EmployeeRoles.CEO],
            EmployeeRoles.DIRECTOR: [EmployeeRoles.CEO]
        }

        if role.name in supervisor_allowed_roles:
            if supervisor.role.name not in supervisor_allowed_roles[role.name]:
                raise ValidationError({
                    "supervisor_id": f"{role.name} can only report to {' or '.join(supervisor_allowed_roles[role.name])}"
                })

    @classmethod
    def _validate_payload(cls, payload, user_id=None):
        cls._validate_unique_email(payload['email'], user_id)
        cls._validate_duplicate_ceo_employee(payload['role_id'], user_id)
        cls.get_user(payload['supervisor_id'])
        cls._get_role(payload['role_id'])
        if payload['department_id']:
            cls._get_department(payload['department_id'])
        cls.validate_selected_supervisor(payload['supervisor_id'], payload['role_id'])

    @classmethod
    def create_user(cls, payload):
        password = payload.pop('password', None)
        cls._validate_payload(payload)
        user = User.objects.create_user(**payload)
        user.set_password(password)
        user.save()
        return user

    @classmethod
    def update_user(cls, payload, employee):
        password = payload.pop('password', None)
        cls._validate_payload(payload, employee.id)
        for key, value in payload.items():
            setattr(employee, key, value)
        employee.save()
        if password:
            employee.set_password(password)
            employee.save()
        return employee

    @classmethod
    def _validate_employee_existing_reportees(cls, employee_id):
        if User.active_objects.filter(supervisor_id=employee_id).exists():
            raise ValidationError(
                'Selected staff is a supervisor to active staff. kindly modify reporting line'
            )

    @classmethod
    def delete_user(cls, employee_id):
        employee=cls.get_user(employee_id)
        cls._validate_employee_existing_reportees(employee_id)
        employee.soft_delete()


class ReportingLineService(AccountService):

    @classmethod
    def get_employee_reporting_line(cls, user_id):
        employee = cls.get_user(user_id)
        reporting_chain = []
        current_user = employee

        while current_user:
            reporting_chain.append(current_user)

            if current_user.supervisor:
                current_user = current_user.supervisor
            else:
                break

        return reporting_chain

    @classmethod
    def get_full_company_hierarchy(cls, request, max_depth=5):
        user = User.active_objects.filter(role__name=EmployeeRoles.CEO).first()
        hierarchy = (
            User.objects
            .filter(id=user.id)
            .prefetch_related(cls._build_prefetch(0, max_depth))
            .first()
        )

        return hierarchy

    @classmethod
    def _build_prefetch(cls, current_depth, max_depth):
        if current_depth >= max_depth:
            return None

        return Prefetch(
            'reportees',
            queryset=User.objects.prefetch_related(
                cls._build_prefetch(current_depth + 1, max_depth)
            )
        )
