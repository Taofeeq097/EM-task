from django.contrib import admin
from accounts.models import Role, User, Department

# Register your models here.

admin.site.register(Role)
admin.site.register(User)
admin.site.register(Department)
