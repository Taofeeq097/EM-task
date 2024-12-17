from django.db.models import TextChoices


class EmployeePositions(TextChoices):
    CEO  = "Chief Executive Officer (CEO)"
    Human_Resources_Manager  = "Human Resources Manager "
    Marketing_Manager  = "Marketing Manager "
    Software_Developer = "Software Developer"
    Customer_Service_Representative = "Customer Service Representative"


class EmployeeRoles(TextChoices):
    EMPLOYEE = "Employee"
    MANAGER = "Manager"
    DIRECTOR =  "Director"
    CEO = "CEO"


class EmployeeDepartments(TextChoices):
    HR = 'Human Resources (HR)'
    Finance_and_Accounting = 'Finance and Accounting'
    Marketing = 'Marketing'
    IT = 'Information Technology (IT)'
    Operations = 'Operations'


class LeaveApprovalStatus(TextChoices):
    APPROVED = 'Approved'
    DECLINED = 'Declined'
    PENDING = 'Pending'
