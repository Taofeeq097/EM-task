from random import choices

from rest_framework import serializers

from base.constants import LeaveApprovalStatus
from leave_management.models import LeaveType, LeaveRequest


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = '__all__'


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_id = serializers.IntegerField(source='employee.id', read_only=True)
    approval_status = serializers.ChoiceField(choices=LeaveApprovalStatus.choices, read_only=True)
    leave_type = serializers.PrimaryKeyRelatedField(queryset=LeaveType.active_objects.all(), required=True)

    class Meta:
        model = LeaveRequest
        fields = ['id', 'leave_type', 'start_date', 'end_date', 'reason', 'employee_id', 'approval_status']

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        if start_date >= end_date:
            raise serializers.ValidationError("Start date must be before the end date.")

        employee = self.context['request'].user
        overlapping_requests = LeaveRequest.active_objects.filter(
            employee=employee,
            start_date__lte=start_date,
            end_date__gte=end_date,
            approval_status__in=[LeaveApprovalStatus.PENDING, LeaveApprovalStatus.APPROVED]
        )
        if overlapping_requests.exists():
            raise serializers.ValidationError(
                "You already have an approved or pending leave request within this time frame."
            )
        data.update({
            "employee": employee,
        })
        return data


class LeaveRequestApprovalSerializer(serializers.Serializer):
    approval_status = serializers.ChoiceField(choices=LeaveApprovalStatus.choices)
    comment = serializers.CharField(allow_blank=True, required=False)
