from django.contrib import admin
from .models import Employees, EmployeesWorkDetails, LeaveManagement, PaySlip, Project, Task

admin.site.register(Employees)
admin.site.register(EmployeesWorkDetails)
admin.site.register(LeaveManagement)
admin.site.register(PaySlip)
admin.site.register(Project)
admin.site.register(Task)
