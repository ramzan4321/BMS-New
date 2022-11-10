import io,os
from django.http import FileResponse
from datetime import datetime, date
import reportlab ,calendar
from django.core.files.storage import FileSystemStorage
from reportlab.pdfgen import canvas
from reportlab.platypus import Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from .models import Employees, LeaveManagement, PaySlip
from django.contrib.auth.models import User


def generate_pdf(user=None):
    date1 = ''.join(e for e in str(datetime.now()) if e.isalnum())
    fileName = f'{user}{date1}.pdf'
    filedir = 'media/pdf_file/'
    filepath = os.path.join(filedir,fileName)

    #----------------- Fetch Data from Database--------------
    uid = User.objects.get(username=user)
    employee = Employees.objects.get(user=uid.id)
    if employee.gender == 'M':
        gender = 'Male'
    else:
        gender = 'Female'
    month = datetime.now().month
    year = datetime.now().year
    if month == 1:
        pre_month = 12
        year = year-1
    else:
        pre_month = month-1
    mnth_name = calendar.month_name[pre_month]
    
    x = LeaveManagement.objects.filter(employee_id=uid.id,leave_type='U',leave_days__month=pre_month).count()
    if x != 0:
        if month == 1:
            day = 22
        elif month <= 8:
            if month % 2 == 0:
                day = 22
            else:
                day = 21
        else:
            if month % 2 == 0:
                day = 21
            else:
                day = 22
        deduction_amount = round((employee.salary / day)*x,2)
        total_salary = round((employee.salary - deduction_amount),2)
    else:
        deduction_amount  = 0.0
        total_salary = employee.salary

    # Testing Temporarily PaySlip
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    c.setFont('Helvetica',18)
    c.setStrokeColor('grey')
    #c.rect(1*inch,9.8*inch,2.1*inch,0.6*inch,fill=0)

    im = Image('media/triodeclogo.png', 1.5*inch ,0.5*inch, hAlign="CENTER")

    im.wrapOn(c, width, height)     
    im.drawOn(c,1*inch, 9.8*inch)

    #c.drawString(1.1*inch,10*inch,'MAiL PLANET')
    c.setFont('Helvetica',14)
    c.drawString(3.5*inch,10.2*inch,'Triodec Solutions')
    c.setFont('Helvetica',12)
    c.drawString(2.8*inch,10*inch,'Prahlad Nagar, Ahmedabad, 380015')
    c.drawString(3.8*inch,9.8*inch,'Gujarat')
    c.setFont('Helvetica',14)
    c.drawString(6.5*inch,10*inch,'PAY SLIP')
    
    c.setLineWidth(1)
    #c.line(1*inch,9.8*inch,3.2*inch,9.8*inch)
    c.line(6*inch,9.8*inch,7.4*inch,9.8*inch)
    c.line(1*inch,9.7*inch,7.4*inch,9.7*inch)

    c.setFillColor('lightgrey')
    c.rect(1*inch,9.3*inch,6.4*inch,0.3*inch,fill=1,stroke=False)
    c.rect(1*inch,8.4*inch,6.4*inch,0.8*inch,fill=0)
    c.setFillColor('black')
    c.setFont('Helvetica',12)
    c.drawString(2.8*inch,9.4*inch,f'Payslip for the month of {mnth_name} {year}')
    c.drawString(1.2*inch,8.9*inch,'Employee Name :')
    c.drawString(3.2*inch,8.9*inch, employee.name)
    c.drawString(5.2*inch,8.9*inch,'Paid Day :')
    c.drawString(6.4*inch,8.9*inch, employee.paid_days)
    c.drawString(1.2*inch,8.5*inch,'Gender :')
    c.drawString(3.2*inch,8.5*inch, gender)
    c.drawString(5.2*inch,8.5*inch,'LOP Day :')
    c.drawString(6.4*inch,8.5*inch,'0')

    c.rect(1*inch,8*inch,6.4*inch,0.3*inch,fill=0)
    c.line(2.6*inch,8*inch,2.6*inch,8.3*inch)
    c.line(4.2*inch,8*inch,4.2*inch,8.3*inch)
    c.line(5.8*inch,8*inch,5.8*inch,8.3*inch)

    c.drawString(1.2*inch,8.1*inch,'Earning')
    c.drawString(3.5*inch,8.1*inch,'Amount')
    c.drawString(4.5*inch,8.1*inch,'Deduction')
    c.drawString(6.1*inch,8.1*inch,'Amount')

    c.rect(1*inch,7.7*inch,6.4*inch,0.3*inch,fill=0)
    c.line(4.2*inch,7.7*inch,4.2*inch,8*inch)

    c.drawString(1.2*inch,7.8*inch,'Basic Pay')
    c.drawString(3.5*inch,7.8*inch, str(employee.salary))
    c.drawString(4.3*inch,7.8*inch,'Leave Deduction')
    c.drawString(6.1*inch,7.8*inch, str(deduction_amount))
    c.drawString(4.3*inch,7.5*inch,'Total Leaves')
    c.drawString(6.3*inch,7.5*inch, str(x))

    c.rect(1*inch,7.1*inch,2.2*inch,0.6*inch,fill=0)
    c.rect(3.2*inch,7.1*inch,1*inch,0.6*inch,fill=0)
    c.line(1*inch,7.4*inch,3.2*inch,7.4*inch)

    c.drawString(1.2*inch,7.5*inch,'OT Hours')
    c.drawString(2.8*inch,7.5*inch,'-')
    c.drawString(1.2*inch,7.2*inch,'OT Rate')
    c.drawString(2.8*inch,7.2*inch,'-')

    c.rect(1*inch,6.8*inch,3.2*inch,0.3*inch,fill=0)
    c.drawString(1.2*inch,6.9*inch,'OT PAYMENT')
    c.drawString(3.6*inch,6.9*inch,'-')

    c.line(4.2*inch,7.4*inch,7.4*inch,7.4*inch)
    c.line(7.4*inch,7.7*inch,7.4*inch,6.8*inch)

    c.rect(1*inch,6.5*inch,6.4*inch,0.3*inch,fill=0)
    c.line(2.6*inch,6.5*inch,2.6*inch,6.8*inch)
    c.line(4.2*inch,6.5*inch,4.2*inch,6.8*inch)
    c.line(5.8*inch,6.5*inch,5.8*inch,6.8*inch)

    c.drawString(1.2*inch,6.6*inch,'Total Payment')
    c.drawString(3.4*inch,6.6*inch, str(employee.salary))
    c.drawString(4.5*inch,6.6*inch,'Total Deduction')
    c.drawString(6*inch,6.6*inch, str(deduction_amount))

    c.rect(1*inch,6.2*inch,6.4*inch,0.3*inch,fill=0)
    c.drawString(1.2*inch,6.3*inch,'Net Pay')
    c.drawString(3.4*inch,6.3*inch, "Rs. "+str(total_salary))

    c.save()

    entry = PaySlip(employee_id = uid, path = filepath, dispatch_date = date.today())
    entry.save()

    fs = FileSystemStorage('')
    
    return FileResponse(fs.open(filepath, 'rb'), filename=fileName)
    #"media/pdf_file/"+f'{user}.pdf'