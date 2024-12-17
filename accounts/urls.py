from django.urls import path

from accounts.views import (
    DepartmentListAPIView,
    EmployeeListCreateView,
    EmployeeReportingLineAPIView,
    LoginAPIView,
    RoleListAPIView,
)

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('', EmployeeListCreateView.as_view(), name='employee_list_create'),
    path('<int:user_id>/hierarchy/', EmployeeReportingLineAPIView.as_view(), name='employee_detail'),
    path('roles/', RoleListAPIView.as_view(), name='role-list'),
    path('departments/', DepartmentListAPIView.as_view(), name='department-list'),
]