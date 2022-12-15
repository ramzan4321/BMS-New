from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.utils import timezone

class CompanyCredentials(models.Model):
    company_name = models.CharField(max_length=100, null=False, blank=False)
    address = models.CharField(max_length=100, null=False, blank=False)
    pincode = models.IntegerField()
    city = models.CharField(max_length=100, null=False, blank=False)
    state = models.CharField(max_length=100, null=False, blank=False)
    budget = models.IntegerField()

    def __str__(self):
        return self.company_name
class CompanyAccount(models.Model):
    title = models.CharField(max_length=100, null=False, blank=False)
    type = models.CharField(max_length=10, null=False, blank=False)
    category = models.CharField(max_length=100, null=False, blank=False)
    date = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()

    def __str__(self):
        return self.title

class Employees(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    EMPLOYEE_CHOICES = (
        ('CEO','CEO'),
        ('MGR','Manager'),
        ('SEE','Senior'),
        ('STE','Standard'),
    )
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=70,null=True, blank=True)
    gender = models.CharField(max_length=6,null=True, blank=True, choices=GENDER_CHOICES)
    dob = models.DateField(null=True, blank=True)
    mobile = models.CharField(max_length=10, null=False, blank=False, default='9999999999')
    address = models.CharField(max_length=70,null=True, blank=True)
    pincode = models.IntegerField(default=208023)
    image = models.ImageField(default='default.jpg', upload_to='profile_img/')
    city = models.CharField(max_length=70,null=True, blank=True)
    state = models.CharField(max_length=70,null=True, blank=True)
    department = models.CharField(max_length=70,null=True, blank=True)
    designation = models.CharField(max_length=70,null=True, blank=True)
    about = models.CharField(max_length=500,null=True, blank=True)
    account_holder_name = models.CharField(max_length=70,null=True, blank=True)
    branch = models.CharField(max_length=70,null=True, blank=True)
    bank_name = models.CharField(max_length=70,null=True, blank=True)
    bank_account_no = models.CharField(max_length=70,null=True, blank=True)
    ifsc_code = models.CharField(max_length=70,null=True, blank=True)
    pan_no = models.CharField(max_length=70,null=True, blank=True)
    pf_no = models.CharField(max_length=70,null=True, blank=True)
    pf_uan = models.CharField(max_length=70,null=True, blank=True)
    role = models.CharField(max_length=3,null=True, blank=True, choices=EMPLOYEE_CHOICES)
    manager = models.ForeignKey('self',on_delete=models.CASCADE,null=True, blank=True)
    salary = models.IntegerField(null=True, blank=True)
    paid_days = models.CharField(max_length=2, null=True, blank=True)

    def __str__(self):
        return self.user.username


class LeaveManagement(models.Model):
    LEAVE_TYPES = (
        ('P', 'Paid'),
        ('U', 'Unpaid'),
    )
    STATUS_CHOICE = (
        ('A','Approved'),
        ('R','Rejected'),
        ('P','Pending'),
    )
    employee_id = models.ForeignKey(User, on_delete=models.CASCADE,related_name='employee_leave')
    leave_reason = models.CharField(max_length=150,null=False,blank=False)
    leave_days = models.DateField()
    leave_type = models.CharField(max_length=1, choices=LEAVE_TYPES)
    status = models.CharField(max_length =25, null=True, blank=True, default='P', choices=STATUS_CHOICE)

    def __str__(self):
        return str(self.employee_id)+" "+str(self.leave_days)+" "+self.leave_type


class PaySlip(models.Model):
    employee_id = models.ForeignKey(User, on_delete=models.CASCADE,related_name='payslip')
    path = models.CharField(max_length =250, null=False, blank=False)
    dispatch_date = models.DateField()
    salary = models.IntegerField(default=0)
    earning = models.IntegerField(default=0)

    def __str__(self) -> str:
        return str(self.employee_id)+" "+str(self.dispatch_date)


class Project(models.Model):
    STATUS_CHOICE = (
        ('N','Not Assigned'),
        ('A','Assigned'),
        ('C','Completed'),
    )
    project_title = models.CharField(max_length =250, null=False, blank=False)
    start_date = models.DateField(auto_now=True)
    status = models.CharField(max_length =25, null=True, blank=True, default='N', choices=STATUS_CHOICE)
    submit_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.project_title

class TaskTitle(models.Model):
    STATUS_CHOICE = (
        ('N','Not Assigned'),
        ('A','Assigned'),
        ('C','Completed'),
    )
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_tasktitle')
    task_title = models.CharField(max_length =250, null=False, blank=False)
    status = models.CharField(max_length =25, null=True, blank=True,default='N', choices=STATUS_CHOICE)
    def __str__(self):
        return self.task_title

class Task(models.Model):
    STATUS_CHOICE = (
        ('A','Assigned'),
        ('C','Completed'),
    )
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_task')
    task_title = models.ForeignKey(TaskTitle, on_delete=models.CASCADE,max_length =250, null=False, blank=False)
    employee_id = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True, related_name="employee_task")
    manager = models.ForeignKey(User,on_delete=models.CASCADE,null=True, blank=True, related_name="manager_task")
    status = models.CharField(max_length =25, null=True, blank=True,default='N', choices=STATUS_CHOICE)
    start_date = models.DateField(auto_now=True)
    submit_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.task_title)+" "+str(self.project_id)


class Contact(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    email = models.EmailField(blank=False, null=False)
    subject = models.CharField(max_length=50, blank=False, null=False)
    message = models.CharField(max_length=500, blank=False, null=False)

    def __str__(self):
        return self.name+" "+str(self.email)


class EmployeesWorkDetails(models.Model):
    STATUS_CHOICE = (
        ('N','Not Assigned'),
        ('A','Assigned'),
        ('C','Completed'),
    )
    employee_id = models.ForeignKey(User, on_delete=models.CASCADE,related_name='employee_work')
    senior_employee_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, max_length=150,null=False,blank=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, max_length=150,null=False,blank=False)
    status = models.CharField(max_length =25, null=True, blank=True,default='N', choices=STATUS_CHOICE)
    start_date = models.DateField(auto_now=True)
    submit_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.employee_id)