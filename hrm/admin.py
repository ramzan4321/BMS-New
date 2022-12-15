from django.contrib import admin
from django.contrib.auth.models import User
from .models import *

class EmployeesAdminInline(admin.StackedInline):
    model = Employees
    extra = 1

admin.site.unregister(User)
class UserAdmin(admin.ModelAdmin):
    inlines = [EmployeesAdminInline]

admin.site.register(User, UserAdmin)

admin.site.register(Employees)
admin.site.register(CompanyCredentials)
admin.site.register(CompanyAccount)
admin.site.register(EmployeesWorkDetails)
admin.site.register(LeaveManagement)
admin.site.register(PaySlip)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Contact)
