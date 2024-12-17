from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from base.constants import EmployeeRoles, EmployeePositions
from base.role_permission import role_position_required
from leave_management.models import LeaveType
from leave_management.serializers import (
    LeaveRequestApprovalSerializer,
    LeaveTypeSerializer,
    LeaveRequestSerializer
)
from leave_management.services import LeaveTypeService, LeaveRequestService


class LeaveTypeCreateListAPIView(APIView):
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsAuthenticated]

    @role_position_required(
        allowed_roles=[EmployeeRoles.CEO],
        allowed_positions=[EmployeePositions.Human_Resources_Manager]
    )
    def post(self, request):
        serializer = LeaveTypeSerializer(data=request.data)
        if serializer.is_valid():
            leave_type = LeaveTypeService().create_leave_type(serializer.validated_data)
            return Response(data=self.serializer_class(leave_type).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        leave_types = LeaveType.active_objects.all()
        serializer = LeaveTypeSerializer(leave_types, many=True)
        return Response(data=serializer.data)


class LeaveTypeDetailAPIView(APIView):
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, leave_type_id):
        leave_type = LeaveTypeService().get_leave_types(leave_type_id)
        return Response(data=self.serializer_class(leave_type).data, status=status.HTTP_200_OK)

    @role_position_required(
        allowed_roles=[EmployeeRoles.CEO],
        allowed_positions=[EmployeePositions.Human_Resources_Manager]
    )
    def put(self, request, leave_type_id):
        serializer = LeaveTypeSerializer(data=request.data)
        if serializer.is_valid():
            leave_type=LeaveTypeService().update_leave_type(leave_type_id, serializer.validated_data)
            return Response(data=self.serializer_class(leave_type).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @role_position_required(
        allowed_roles=[EmployeeRoles.CEO],
        allowed_positions=[EmployeePositions.Human_Resources_Manager]
    )
    def delete(self, request, leave_type_id):
        LeaveTypeService().delete_leave_type(leave_type_id)
        return Response(data=None, status=status.HTTP_200_OK)


class LeaveRequestCreateAPIView(APIView):
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            leave_request = serializer.save()
            return Response(data=self.serializer_class(leave_request).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        qs = LeaveRequestService().get_leave_requests(request)
        serializer = LeaveRequestSerializer(qs, many=True)
        return Response(data=serializer.data)


class LeaveRequestApprovalAPIView(APIView):
    serializer_class = LeaveRequestApprovalSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, leave_request_id):
        serializer = LeaveRequestApprovalSerializer(data=request.data)
        if serializer.is_valid():
            data = LeaveRequestService().approve_leave_request(serializer.validated_data, leave_request_id, request)
            return Response(data=LeaveRequestSerializer(data).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)










