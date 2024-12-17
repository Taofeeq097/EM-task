from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from accounts.models import User, Role, Department
from accounts.serializers import LoginSerializer, ReportingChainSerializer, UserSerializer, UserHierarchySerializer, \
    RoleSerializer, DepartmentSerializer
from accounts.services import AccountService, ReportingLineService
from base.constants import EmployeeRoles, EmployeePositions
from base.pagination import CustomPagination
from base.role_permission import role_position_required


class LoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class RoleListAPIView(ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Role.active_objects.all()
    serializer_class = RoleSerializer
    pagination_class = CustomPagination

class DepartmentListAPIView(ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Department.active_objects.all()
    serializer_class = DepartmentSerializer
    pagination_class = CustomPagination


class EmployeeListCreateView(APIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination

    @role_position_required(
        allowed_roles=[EmployeeRoles.CEO.value],
        allowed_positions=[EmployeePositions.Human_Resources_Manager.value]
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = AccountService().create_user(serializer.validated_data)
            user_serializer = self.serializer_class(user)
            return Response(user_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @role_position_required(
        allowed_roles=[EmployeeRoles.CEO.value],
        allowed_positions=[EmployeePositions.Human_Resources_Manager.value]
    )
    def get(self, request, *args, **kwargs):
        employees = User.active_objects.all()
        paginator = self.pagination_class()
        paginated_employees = paginator.paginate_queryset(employees, request, view=self)
        serializer = self.serializer_class(paginated_employees, many=True)
        return paginator.get_paginated_response(serializer.data)


class EmployeeDetailAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @role_position_required(
        allowed_roles=[EmployeeRoles.CEO],
        allowed_positions=[EmployeePositions.Human_Resources_Manager]
    )
    def get(self, request, user_id, *args, **kwargs):
        employee = AccountService().get_user(user_id)
        serializer = UserSerializer(employee)
        return Response(serializer.data)

    @role_position_required(
        allowed_roles=[EmployeeRoles.CEO],
        allowed_positions=[EmployeePositions.Human_Resources_Manager]
    )
    def put(self, request, user_id, *args, **kwargs):
        employee = AccountService().get_user(user_id)
        serializer = UserSerializer(employee, data=request.data, partial=True)
        if serializer.is_valid():
            data = AccountService().update_user(serializer.validated_data, employee)
            return Response(UserSerializer(data), status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @role_position_required(
        allowed_roles=[EmployeeRoles.CEO],
        allowed_positions=[EmployeePositions.Human_Resources_Manager]
    )
    def delete(self, request, user_id, *args, **kwargs):
        AccountService().delete_user(user_id)
        return Response({"detail": "Employee deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class EmployeeReportingLineAPIView(APIView):
    serializer_class = ReportingChainSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, user_id, *args, **kwargs):
        data =ReportingLineService().get_employee_reporting_line(user_id)
        return Response(data=self.serializer_class(data, many=True).data, status=status.HTTP_200_OK)


class CompanyHierarchyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        hierarchy = ReportingLineService().get_full_company_hierarchy(request)
        serializer = UserHierarchySerializer(hierarchy)
        return Response(serializer.data)





