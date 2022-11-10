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
        print(employee)
        emp_email = User.objects.get(username=employee.user)
        email = [emp_email.email]
        email.append(ceo_email)
        email_subject = 'Payslip'
        email_body = "Triodec PaySlip"
        payslip(user=emp_email.username)
        email = EmailMessage(
                subject = email_subject,
                body = email_body,
                from_email = 'ramzanalitrux@gmail.com',
                to = email
            )
        query = PaySlip.objects.filter(employee_id=emp_email).last()
        pdf_path = query.path
        email.attach_file(pdf_path)
        #email.attach_file("media/pdf_file/"+f'{emp_email.username}.pdf')
        email.send()
    return "Email Send..."

    #--------------------------------- Start Celery--------------------------------------------

    # celery -A business_management_system worker -l info --pool=solo

    #---------------------------------- Start Celery Beat -------------------------------------

    # celery -A business_management_system beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler

    #---------------------------- That's it ---------------------------------------------------
