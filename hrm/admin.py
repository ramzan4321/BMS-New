from django.contrib import admin
from django.contrib.auth.models import User
from .models import Employees, EmployeesWorkDetails, LeaveManagement, PaySlip, Project, Task

class EmployeesAdminInline(admin.StackedInline):
    model = Employees
    extra = 1

admin.site.unregister(User)
class UserAdmin(admin.ModelAdmin):
    inlines = [EmployeesAdminInline]

admin.site.register(User, UserAdmin)

admin.site.register(Employees)
admin.site.register(EmployeesWorkDetails)
admin.site.register(LeaveManagement)
admin.site.register(PaySlip)
admin.site.register(Project)
admin.site.register(Task)
