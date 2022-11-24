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
from .numtoword import numtowords


def generate_pdf(user=None):
    #-------------------------- Generate unique filename using timestamp--------------------------
    date1 = ''.join(e for e in str(datetime.now()) if e.isalnum())
    fileName = f'{user}{date1}.pdf'
    #-------------------------- End Generate unique filename using timestamp----------------------


    #-------------------------- Define Filepath where PDF Save -----------------------------------
    #fileName = f'{user}.pdf'
    filedir = 'media/pdf_file/'
    filepath = os.path.join(filedir,fileName)
    #--------------------------End Define Filepath where PDF Save --------------------------------


    #------------------------- Fetch Data from Database-------------------------------------------
    uid = User.objects.get(username=user)
    x, xy, leave_paid, day = 0, 0, 0, 0
    employee = Employees.objects.get(user=uid.id)
    if employee.gender == 'M':
        gender = 'Male'
    else:
        gender = 'Female'

    bank_name = "-"
    bank_account_no = "-"
    ifsc_code = "-"
    pan_no = "-"
    pf_no = "-"
    pf_uan = "-"
    if employee.bank_name is not None:
        bank_name =employee.bank_name
    if employee.bank_account_no is not None:
        bank_account_no =employee.bank_account_no
    if employee.ifsc_code is not None:
        ifsc_code =employee.ifsc_code
    if employee.pan_no is not None:
        pan_no =employee.pan_no
    if employee.pf_no is not None:
        pf_no =employee.pf_no
    if employee.pf_uan is not None:
        pf_uan =employee.pf_uan

    #------------------------- Leave management ---------------------------------------------------    
    month = datetime.now().month
    year = datetime.now().year
    if month == 1:
        pre_month = 12
        year = year-1
        y = LeaveManagement.objects.filter(employee_id=uid.id,leave_type='P',leave_days__year=year).count()
        yy = (uid.date_joined).date().year
        if year - yy >= 2:
            bpl = 12
        else:
            bpl = 12 - (uid.date_joined).date().month
        if y < bpl:
            z = bpl-y
            if z > 3:
                xy = z-3
                leave_paid = int((employee.salary/22)*xy)
    else:
        leave_paid = int(0.0)
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
        deduction_amount = int((employee.salary / day)*x)
        total_salary = int((employee.salary - deduction_amount)+leave_paid)
    else:
        deduction_amount  = int(0.0)
        total_salary = int(employee.salary+leave_paid)

    salar_in_words = numtowords(total_salary)
    payslip_date = '01'
    lop = ""
    if len(str(x)) > 1:
        lop += str(x)
    else:
        lop += '0'+str(x)

    ewd = ""
    if len(str(day)) > 1:
        ewd += str(day)
    else:
        ewd += '0'+str(day)

    dop = ""
    if len(str(day-x)) > 1:
        dop += str(day-x)
    else:
        dop += '0'+str(day-x)
    #---------------------------- End Leave Management ------------------------------------------
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    pdfmetrics.registerFont(TTFont('LSB', os.path.join('media/font', 'LiberationSerif-Bold.ttf')))
    pdfmetrics.registerFont(TTFont('LSR', os.path.join('media/font', 'LiberationSerif-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('LSRI', os.path.join('media/font', 'LiberationSerif-Italic.ttf')))
    pdfmetrics.registerFont(TTFont('LSBI', os.path.join('media/font', 'LiberationSerif-BoldItalic.ttf')))
    pdfmetrics.registerFont(TTFont('TRN', 'times.ttf'))
    pdfmetrics.registerFont(TTFont('TRB', 'timesbd.ttf'))

    #---------------------------- Generate Payslip PDF ------------------------------------------
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    c.setFont('LSB',11)
    c.setStrokeColor('grey')
    
    c.setLineWidth(1)
    c.setStrokeColor('black')
    c.rect(0.6*inch,7*inch,7.3*inch,3.4*inch,fill=0,stroke=True)
    c.line(0.6*inch,9.6*inch,7.9*inch,9.6*inch)
    c.line(0.6*inch,8.3*inch,7.9*inch,8.3*inch)
    c.line(0.6*inch,8.05*inch,7.9*inch,8.05*inch)
    c.line(0.6*inch,7.8*inch,7.9*inch,7.8*inch)
    c.line(0.6*inch,7.55*inch,7.9*inch,7.55*inch)
    c.line(4.2*inch,9.6*inch,4.2*inch,7.55*inch)
    
    im = Image('media/01.png', 0.57*inch ,0.62*inch, hAlign="CENTER")   
    im.wrapOn(c, width, height)           
    im.drawOn(c,0.8*inch, 9.7*inch)
    

    c.drawString(3.5*inch,10.17*inch,'Triodec Solutions LLP')
    c.setFont('LSR',7)
    c.drawString(3.1*inch,10.01*inch,'PRAHLADNAGAR, AHMEDABAD, GUJARAT -')
    c.setFont('LSR',8)
    c.drawString(5.2*inch,10.01*inch,'380015')
    c.setFont('LSB',12)
    c.drawString(3.3*inch,9.75*inch,f'PAYSLIP - {payslip_date} {(mnth_name[0:3]).upper()} {year}')
    
    c.setFont('LSR',9)
    c.drawString(0.65*inch,9.45*inch,'Employee Name:')
    c.drawString(0.65*inch,9.27*inch,'Joining Date:')
    c.drawString(0.65*inch,9.09*inch,'Designation:')
    c.drawString(0.65*inch,8.91*inch,'Department:')
    c.drawString(0.65*inch,8.72*inch,'Effective Work Days:')
    c.drawString(0.65*inch,8.54*inch,'Loss of Pay Days:')
    c.drawString(0.65*inch,8.36*inch,'Days Payable:')

    #date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")

    c.setFont('LSR',9)
    c.drawString(2.25*inch,9.45*inch, employee.name)
    c.drawString(2.25*inch,9.27*inch, str((employee.user.date_joined).date().strftime("%d %B %Y")))
    c.drawString(2.25*inch,9.09*inch, employee.designation)
    c.drawString(2.25*inch,8.91*inch, employee.department)
    c.drawString(2.25*inch,8.72*inch, ewd)
    c.drawString(2.25*inch,8.54*inch, lop)
    c.drawString(2.25*inch,8.36*inch, dop)

    c.setFont('LSR',9)
    c.drawString(4.25*inch,9.45*inch,'Employee No:')
    c.drawString(4.25*inch,9.27*inch,'Bank Name:')
    c.drawString(4.25*inch,9.09*inch,'Bank Account No:')
    c.drawString(4.25*inch,8.91*inch,'IFSC Code:')
    c.drawString(4.25*inch,8.72*inch,'PAN Number:')
    c.drawString(4.25*inch,8.54*inch, 'PF No:')
    c.drawString(4.25*inch,8.36*inch,'PF UAN:')

    c.setFont('LSR',9)
    c.drawString(6.05*inch,9.45*inch,str(employee.user.pk))
    c.drawString(6.05*inch,9.27*inch, str(bank_name))
    c.drawString(6.05*inch,9.09*inch, str(bank_account_no))
    c.drawString(6.05*inch,8.91*inch, str(ifsc_code))
    c.drawString(6.05*inch,8.72*inch, str(pan_no))
    c.drawString(6.05*inch,8.54*inch, str(pf_no))
    c.drawString(6.05*inch,8.36*inch, str(pf_uan))

    c.setFont('LSB',10)
    c.drawString(0.65*inch,8.1*inch,'Earnings')
    c.setFont('LSR',9)
    c.drawString(0.65*inch,7.85*inch,'Basic')
    c.drawString(0.65*inch,7.6*inch,'Total Earning:')

    c.setFont('LSB',10)
    c.drawString(2.5*inch,8.1*inch,'Actual')
    c.setFont('LSR',9)
    c.drawString(2.55*inch,7.85*inch, str(int(employee.salary)))
    c.drawString(2.55*inch,7.6*inch, str(int(employee.salary)))

    c.setFont('LSB',10)
    c.drawString(3.5*inch,8.1*inch,'Earned')
    c.setFont('LSR',9)
    c.drawString(3.55*inch,7.85*inch, str(total_salary))
    c.drawString(3.55*inch,7.6*inch, str(total_salary))

    c.setFont('LSB',10)
    c.drawString(4.25*inch,8.1*inch,'Deduction')
    c.setFont('LSR',9)
    c.drawString(4.25*inch,7.85*inch,'Prof. Tax')
    c.drawString(4.25*inch,7.6*inch,'Total Deduction:')

    c.setFont('LSB',10)
    c.drawString(7.15*inch,8.1*inch,'Amount')
    c.setFont('LSR',9)
    c.drawString(7.25*inch,7.85*inch, '0')
    c.drawString(7.25*inch,7.6*inch, '0')

    c.drawString(0.65*inch,7.3*inch,'Net Pay For The Month ( Total Earnings - Total Deductions):')
    c.setFont('LSB',10)
    c.drawString(3.8*inch,7.3*inch, str(total_salary))
    c.setFont('LSB',10)
    c.drawString(0.65*inch,7.05*inch, "Amount in words :")
    c.setFont('LSRI',9)
    c.drawString(1.8*inch,7.05*inch, salar_in_words.title()+" Only.")

    c.setFont('LSB',10)
    c.drawString(0.6*inch,6.8*inch,'**Note')
    c.setFont('LSR',9)
    c.drawString(1*inch,6.8*inch,' : All amounts displayed in this payslip are in')
    c.setFont('LSB',10)
    c.drawString(3.3*inch,6.8*inch,'INR.')
    c.setFont('LSR',9)
    c.drawString(0.6*inch,6.6*inch,'*This is computer generated statement, does not require signature.')



    '''
    width, height = letter
    c.setFont('Helvetica',18)
    c.setStrokeColor('grey')
                                                                            #------,
    im = Image('media/triodeclogo.png', 1.5*inch ,0.5*inch, hAlign="CENTER")       #
    im.wrapOn(c, width, height)                                                    # Add Logo in PDF
    im.drawOn(c,1*inch, 9.8*inch)                                                  #
                                                                            #------'
    c.setFont('Helvetica',14)
    c.drawString(3.5*inch,10.2*inch,'Triodec Solutions')
    c.setFont('Helvetica',12)
    c.drawString(2.8*inch,10*inch,'Prahlad Nagar, Ahmedabad, 380015')
    c.drawString(3.8*inch,9.8*inch,'Gujarat')
    c.setFont('Helvetica',14)
    c.drawString(6.5*inch,10*inch,'PAY SLIP')
    
    c.setLineWidth(1)
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

    c.drawString(1.2*inch,7.5*inch,'Balanced Leaves')
    c.drawString(2.8*inch,7.5*inch, str(xy))
    c.drawString(1.2*inch,7.2*inch,'Per Leaves')
    c.drawString(2.5*inch,7.2*inch,str(round(employee.salary/22,2)))

    c.rect(1*inch,6.8*inch,3.2*inch,0.3*inch,fill=0)
    c.drawString(1.2*inch,6.9*inch,'Leaves Payment')
    c.drawString(3.4*inch,6.9*inch, str(leave_paid))

    c.line(4.2*inch,7.4*inch,7.4*inch,7.4*inch)
    c.line(7.4*inch,7.7*inch,7.4*inch,6.8*inch)

    c.rect(1*inch,6.5*inch,6.4*inch,0.3*inch,fill=0)
    c.line(2.6*inch,6.5*inch,2.6*inch,6.8*inch)
    c.line(4.2*inch,6.5*inch,4.2*inch,6.8*inch)
    c.line(5.8*inch,6.5*inch,5.8*inch,6.8*inch)

    c.drawString(1.2*inch,6.6*inch,'Total Payment')
    c.drawString(3.4*inch,6.6*inch, str(employee.salary+leave_paid))
    c.drawString(4.5*inch,6.6*inch,'Total Deduction')
    c.drawString(6*inch,6.6*inch, str(deduction_amount))

    c.rect(1*inch,6.2*inch,6.4*inch,0.3*inch,fill=0)
    c.setFont('Helvetica-Bold',12)
    c.drawString(1.2*inch,6.3*inch,'Net Pay')
    c.drawString(3.4*inch,6.3*inch, "Rs. "+str(total_salary))
    '''
    c.save()

    ex = PaySlip.objects.filter(employee_id = uid, dispatch_date = date.today()).exists()
    if ex == False:
        entry = PaySlip(employee_id = uid, path = filepath, dispatch_date = date.today())
        entry.save()

    fs = FileSystemStorage('')
    
    return FileResponse(fs.open(filepath, 'rb'), filename=fileName)

    #----------------------------- End Generate Payslip pdf -------------------------------------