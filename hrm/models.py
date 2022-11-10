from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Employees(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    EMPLOYEE_CHOICES =(
        ('CEO','CEO'),
        ('MGR','Manager'),
        ('SEE','Senior'),
        ('STE','Standard'),
    )
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=70,null=True, blank=True)
    gender = models.CharField(max_length=6,null=True, blank=True, choices=GENDER_CHOICES)
    dob = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=70,null=True, blank=True)
    image = models.ImageField(default='default.jpg', upload_to='profile_img/')
    city = models.CharField(max_length=70,null=True, blank=True)
    state = models.CharField(max_length=70,null=True, blank=True)
    department = models.CharField(max_length=70,null=True, blank=True)
    designation = models.CharField(max_length=70,null=True, blank=True)
    role = models.CharField(max_length=3,null=True, blank=True, choices=EMPLOYEE_CHOICES)
    manager = models.ForeignKey('self',on_delete=models.CASCADE,null=True, blank=True)
    salary = models.FloatField(null=True, blank=True)
    paid_days = models.CharField(max_length=70, null=True, blank=True)

    def __str__(self):
        return self.user.username

class EmployeesWorkDetails(models.Model):
    employee_id = models.ForeignKey(User, on_delete=models.CASCADE,related_name='employee_work')
    working_day = models.DateField()
    task = models.CharField(max_length=150,null=False,blank=False)
    project = models.CharField(max_length=150,null=False,blank=False)
    end_day_time = models.DateTimeField()

    def __str__(self):
        return str(self.employee_id)

class LeaveManagement(models.Model):
    LEAVE_TYPES = (
        ('P', 'Paid'),
        ('U', 'Unpaid'),
    )
    employee_id = models.ForeignKey(User, on_delete=models.CASCADE,related_name='employee_leave')
    leave_reason = models.CharField(max_length=150,null=False,blank=False)
    leave_days = models.DateField()
    leave_type = models.CharField(max_length=1, choices=LEAVE_TYPES)

    def __str__(self):
        return str(self.employee_id)


class PaySlip(models.Model):
    employee_id = models.ForeignKey(User, on_delete=models.CASCADE,related_name='payslip')
    path = models.CharField(max_length =250, null=False, blank=False)
    dispatch_date = models.DateField()

    def __str__(self) -> str:
        return str(self.employee_id)+" "+str(self.dispatch_date)

