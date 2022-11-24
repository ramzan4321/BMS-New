from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from .models import Employees, PaySlip
from .payslip_pdf import generate_pdf as payslip

def send_review_email():
    #employees = Employees.objects.exclude(role='CEO')
    employees = Employees.objects.filter(user__username='Ramzan123')
    ceo_query = Employees.objects.filter(role='CEO').values('user__email')
    ceo_email = ceo_query[0]['user__email']

    for employee in employees:
        #emp_email = User.objects.get(username=employee.user)
        email_ = [employee.user.email]
        #email_.append(ceo_email)
        email_subject = 'Payslip'
        email_body = "Triodec PaySlip"
        payslip(user=employee.user.username)
        email = EmailMessage(
                subject = email_subject,
                body = email_body,
                from_email = 'ramzanalitrux@gmail.com',
                to = email_
            )
        query = PaySlip.objects.filter(employee_id=employee.user).last()
        pdf_path = query.path
        email.attach_file(pdf_path)
        #email.attach_file("media/pdf_file/"+f'{emp_email.username}.pdf')
        email.send()
    return "Email Send..."

def send_leave_email(data):
    email_subject = data['subject']
    email_body = data['body']
    from_email = data['employee_email']
    ceo_query = Employees.objects.filter(role='CEO').values('user__email')
    ceo_email = ceo_query[0]['user__email']
    email = EmailMessage(
                subject = email_subject,
                body = email_body,
                from_email = from_email,
                to = ['aliramzan982@gmail.com',]
            )
    email.send()

def send_leave_email_to_employee(data):
    email_subject = data['subject']
    email_body = data['body']
    to_email = data['employee_email']
    ceo_query = Employees.objects.filter(role='CEO').values('user__email')
    ceo_email = ceo_query[0]['user__email']
    email = EmailMessage(
                subject = email_subject,
                body = email_body,
                from_email = ceo_email,
                to = to_email,
            )
    email.send()

    #--------------------------------- Start Celery--------------------------------------------

    # celery -A business_management_system worker -l info --pool=solo

    #---------------------------------- Start Celery Beat -------------------------------------

    # celery -A business_management_system beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler

    #---------------------------- That's it ---------------------------------------------------
