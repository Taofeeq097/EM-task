from django.db import models
from accounts.models import User
from base.constants import LeaveApprovalStatus, EmployeeRoles
from base.models import BaseModel

# Create your models here.
class LeaveType(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name



class LeaveRequest(BaseModel):
    leave_type = models.ForeignKey(LeaveType, on_delete=models.SET_NULL, null=True, blank=True)
    employee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    approval_status = models.CharField(
        max_length=255,
        choices=LeaveApprovalStatus.choices,
        default=LeaveApprovalStatus.PENDING
    )
    action_on = models.DateTimeField(null=True, blank=True)
    reason = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.leave_type.name} - {self.start_date} - {self.end_date}'


class LeaveApprovalFlow(BaseModel):
    leave_request = models.ForeignKey(LeaveRequest, on_delete=models.SET_NULL, null=True, blank=True)
    approval_officer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField(max_length=50, choices=EmployeeRoles.choices, default=EmployeeRoles.MANAGER)
    approval_status = models.CharField(max_length=255, choices=LeaveApprovalStatus.choices,
                                       default=LeaveApprovalStatus.PENDING)
    comment = models.TextField(null=True, blank=True)
    action_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.leave_request} - {self.approval_status}'








