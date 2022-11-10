from django.contrib import admin
from .models import Employees, EmployeesWorkDetails, LeaveManagement, PaySlip

admin.site.register(Employees)
admin.site.register(EmployeesWorkDetails)
admin.site.register(LeaveManagement)
admin.site.register(PaySlip)
