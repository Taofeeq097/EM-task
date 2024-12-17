from django.urls import path

from accounts.views import (
    EmployeeListCreateView,
    EmployeeReportingLineAPIView,
    LoginAPIView
)

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('', EmployeeListCreateView.as_view(), name='employee_list_create'),
    path('<int:user_id>/hierarchy/', EmployeeReportingLineAPIView.as_view(), name='employee_detail')
]