from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        user = authenticate(username=data.get('email'), password=data.get('password'))
        if not user:
            raise serializers.ValidationError("Invalid username or password.")

        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "full_name": user.get_complete_name,
                "email": user.email,
            },
        }


class UserSerializer(serializers.ModelSerializer):
    supervisor_id = serializers.IntegerField(write_only=True)
    role_id = serializers.IntegerField(write_only=True)
    department_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    email = serializers.EmailField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'middle_name', 'first_name', 'last_name',
            'role_id', 'phone_number', 'position',
            'supervisor_id', 'department_id', 'password',
        ]
        extra_kwargs = {
            'email': {'read_only': True},
            'password': {'write_only': True},
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['supervisor'] = instance.supervisor.get_complete_name if instance.supervisor else None
        representation['role'] = instance.role.name if instance.role else None
        representation['department'] = instance.department.name if instance.department else None
        return representation


class ReportingChainSerializer(serializers.ModelSerializer):
    supervisor_id = serializers.IntegerField(source='supervisor.id', required=False)
    role = serializers.CharField(source='role.name')
    position = serializers.CharField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'role', 'position', 'supervisor_id']


class UserHierarchySerializer(serializers.ModelSerializer):
    reports = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'position',
            'department',
            'reports'
        ]

    def get_reports(self, obj):
        reportees = obj.reportees.all()
        if not reportees:
            return []
        return UserHierarchySerializer(reportees, many=True).data