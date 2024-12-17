from django.contrib import admin

from leave_management.models import LeaveType, LeaveRequest, LeaveApprovalFlow

# Register your models here.

admin.site.register(LeaveType)
admin.site.register(LeaveRequest)
admin.site.register(LeaveApprovalFlow)