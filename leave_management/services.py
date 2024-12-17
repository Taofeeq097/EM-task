from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from accounts.services import AccountService
from base.constants import LeaveApprovalStatus, EmployeeRoles
from leave_management.models import LeaveType, LeaveRequest, LeaveApprovalFlow


class LeaveTypeService:

    @classmethod
    def get_leave_types(cls, leave_type_id):
        try:
            return LeaveType.active_objects.filter(id=leave_type_id)
        except LeaveType.DoesNotExist:
            raise ValidationError(f'Leave type with ID {leave_type_id} does not exists')

    @classmethod
    def _validate_leave_name(cls, leave_type_name, leave_type_id=None):
        duplicated_leave = LeaveType.active_objects.filter(name=leave_type_name)
        if leave_type_id:
            duplicated_leave.exclude(id=leave_type_id)
        if duplicated_leave.exists():
            raise ValidationError(f"LeaveType {leave_type_name} already exists")

    @classmethod
    def create_leave_type(cls, payload):
        leave_type_name = payload['name']
        cls._validate_leave_name(leave_type_name)
        return LeaveType.active_objects.create(**payload)

    @classmethod
    def update_leave_type(cls, leave_type_id, payload):
        leave_type = cls.get_leave_types(leave_type_id)
        cls._validate_leave_name(leave_type.name)
        for key, value in payload.items():
            setattr(leave_type, key, value)
        leave_type.save()
        return leave_type

    @classmethod
    def delete_leave_type(cls, leave_type_id):
        leave_type = cls.get_leave_types(leave_type_id)
        if LeaveRequest.active_objects.filter(
                leave_type_id=leave_type_id,
                approval_status__in=[LeaveApprovalStatus.APPROVED, LeaveApprovalStatus.PENDING]
            ).exists():
            raise ValidationError(f"Cannot delete!, there are active leave requests on this leave type")
        leave_type.soft_delete()


class LeaveRequestService(AccountService):

    @classmethod
    def get_leave_request(cls, request_id):
        try:
            return LeaveRequest.active_objects.get(id=request_id)
        except LeaveRequest.DoesNotExist:
            raise ValidationError(f'Request with ID {request_id} does not exists')

    @classmethod
    def get_leave_requests(cls, request):
        user = request.user
        user_role_name = cls._get_role(user.role.id).name
        role_access_filters = {
            EmployeeRoles.CEO: Q(),
            EmployeeRoles.MANAGER: Q(employee__supervisor_id=user.id),
            EmployeeRoles.DIRECTOR: Q(employee__supervisor_id=user.id) | Q(employee__supervisor__supervisor_id=user.id),
            EmployeeRoles.EMPLOYEE: Q(employee_id=user.id),
        }
        query_filter = role_access_filters.get(user_role_name, Q(employee_id=user.id))
        query_filter |= Q(employee_id=user.id)
        return LeaveRequest.active_objects.filter(query_filter)

    @classmethod
    def _validate_approval_status(cls, approval_status, leave_request_id, request):
        if LeaveApprovalFlow.active_objects.filter(
                leave_request_id=leave_request_id,
                approval_status=approval_status,
                approval_officer_id=request.user.id
        ).exists():
            raise ValidationError(f'You have already {approval_status} this leave request')

    @classmethod
    def _validate_manager_approval(cls, leave_request_id):
        manager_approval_exists = LeaveApprovalFlow.active_objects.filter(
            leave_request_id=leave_request_id,
            role=EmployeeRoles.MANAGER,
            approval_status=LeaveApprovalStatus.APPROVED
        ).exists()
        if not manager_approval_exists:
            raise ValidationError("Pending Employee Manager Approval")

    @classmethod
    def _process_leave_approval(cls, payload, leave_request_id, request):
        leave_request = cls.get_leave_request(leave_request_id)
        requester = cls.get_user(leave_request.employee_id)
        if requester.role.name == EmployeeRoles.EMPLOYEE:
            if request.user.role.name == EmployeeRoles.MANAGER and request.user.id == request.supervisor_id:
                cls.get_or_created_new_approval_flow(leave_request_id, request, payload)

            elif request.user.role.name in [EmployeeRoles.DIRECTOR, EmployeeRoles.CEO]:
                if request.user.role.name == EmployeeRoles.DIRECTOR and request.user.id == requester.supervisor.supervisor_id if requester.supervisor.supervisor_id else None:
                    cls._validate_manager_approval(leave_request_id)
                cls.get_or_created_new_approval_flow(leave_request_id, request, payload, influence_req_obj=True)

        elif requester.role.name == EmployeeRoles.MANAGER:
            if request.user.role.name in [EmployeeRoles.DIRECTOR, EmployeeRoles.CEO]:
                if  request.user.role.name == EmployeeRoles.DIRECTOR and not request.user.id == requester.supervisor.id:
                    raise ValidationError(f"You cannot approve this leave request")
                cls.get_or_created_new_approval_flow(leave_request_id, request, payload, influence_req_obj=True)

        elif requester.role.name == EmployeeRoles.DIRECTOR and request.user.role.name == EmployeeRoles.CEO:
            cls.get_or_created_new_approval_flow(leave_request_id, request, payload, influence_req_obj=True)

        else:
            raise ValidationError(f"Invalid request, Kindly reset requester reporting line")

    @classmethod
    def get_or_created_new_approval_flow(cls, leave_request_id, request, payload, influence_req_obj=False):
        approval_flow, created = LeaveApprovalFlow.active_objects.get_or_create(
            leave_request_id=leave_request_id,
            approval_officer_id=request.user.id,
            role=request.user.role.name
        )
        approval_flow.comment = payload.get('comment', None)
        approval_flow.approval_status = payload['approval_status']
        approval_flow.save()

        if influence_req_obj:
            leave_request = cls.get_leave_request(leave_request_id)
            leave_request.approval_status = payload['approval_status']
            leave_request.action_on = timezone.now()
            leave_request.save()

    @classmethod
    def approve_leave_request(cls, payload, leave_request_id, request):
        leave_request = cls.get_leave_request(leave_request_id)
        if leave_request.employee_id == request.user.id:
            raise ValidationError('Invalid request!, you cannot approve your own leave request.')

        cls._validate_approval_status(payload['approval_status'], leave_request_id, request)
        cls._process_leave_approval(payload, leave_request_id, request)

        return leave_request









