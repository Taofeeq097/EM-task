from django.urls import path

from leave_management.views import (
    LeaveRequestCreateAPIView,
    LeaveRequestApprovalAPIView,
    LeaveTypeCreateListAPIView
)


urlpatterns = [
    path('', LeaveRequestCreateAPIView.as_view(), name='leave-request-create'),
    path('<int:leave_request_id>/', LeaveRequestApprovalAPIView.as_view(), name='leave-request-approval'),
    path('leave-types/', LeaveTypeCreateListAPIView.as_view(), name='leave-type-list'),

]