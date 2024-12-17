from django.db import models
from django.contrib.auth.models import AbstractUser
from base.constants import EmployeePositions, EmployeeRoles
from base.models import BaseModel
from base.managers import ActiveManager, UserManager
from phonenumber_field.modelfields import PhoneNumberField


class Role(BaseModel):
    name = models.CharField(max_length=200, unique=True, choices=EmployeeRoles.choices)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Department(BaseModel):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class User(BaseModel, AbstractUser):
    email = models.EmailField(verbose_name="email address", unique=True)
    middle_name = models.CharField(max_length=200, null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = PhoneNumberField(null=False, blank=True)
    position = models.CharField(
        max_length=100,
        choices=EmployeePositions.choices
    )
    supervisor = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='reportees')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    objects = UserManager()
    active_objects = ActiveManager()

    def __str__(self):
        return self.email

    @property
    def get_complete_name(self):
        first_and_middle_name = (
            self.first_name + f" {self.middle_name}"
            if self.middle_name
            else self.first_name
        )
        complete_name = "%s %s" % (first_and_middle_name, self.last_name)
        return complete_name.strip()




