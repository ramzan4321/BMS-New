from django.shortcuts import render, redirect
from .forms import UserRegisterForm, EmailForm, UserUpdateForm, WorkForm, LeaveForm
from django.contrib import messages
from .models import Employees, EmployeesWorkDetails,LeaveManagement, PaySlip
from django.contrib.auth.models import User
from django.http import FileResponse
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required

from datetime import datetime, date
from django.core.files.storage import FileSystemStorage
from django.utils import timezone    
from .payslip_pdf import generate_pdf as payslip


def index(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        print(form.errors)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f'{username}! Welcome to the MAil Planet...')
            return redirect('index')
    elif request.user.is_authenticated:
        return redirect('profile')
    form = UserRegisterForm()
    e_form = EmailForm()
    context = {
        'form':form,
        'e_form':e_form,
    }
    print("end")
    return render(request, 'hrm/index.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, request.FILES, instance=request.user.employees)
        w_form = WorkForm(request.POST)
        l_form = LeaveForm(request.POST)
        if u_form.is_valid():
            print(u_form.errors)
            u_form.save()
            messages.success(request,'Your profile has been updated...')
            return redirect('profile')
        elif w_form.is_valid():
            form = w_form.save(commit=False)
            form.employee_id = request.user
            form.save()
            messages.success(request,'Your work status has been submitted...')
            return redirect('profile')
        elif l_form.is_valid():
            leave_type = l_form.cleaned_data.get('leave_type')
            date_split = l_form.cleaned_data.get('leave_days')
            year, month, day = str(date_split).split('-')
            day_name = date(int(year), int(month), int(day))
            week_day = day_name.strftime("%A")

            if week_day == 'Sunday' or week_day == 'Saturday' or date.today() > date_split:
                messages.warning(request,'Sorry! No need for leaves on weekend or past dates.')
                return redirect('profile')

            if LeaveManagement.objects.filter(employee_id = request.user, leave_days = date_split).exists():
                messages.warning(request,'Sorry! You have taken leave already.')
                return redirect('profile')

            if leave_type == 'P':
                year = datetime.now().year
                chk = LeaveManagement.objects.filter(employee_id=request.user,leave_type='P',leave_days__year=year).count()
                usr = User.objects.get(username=request.user)
                date_joined = usr.date_joined
                if date_joined.date().year < year:
                    chk_last_year = LeaveManagement.objects.filter(employee_id=request.user,leave_type='P',leave_days__year=(year-1)).count()
                    if chk_last_year < 12:
                        balance_leave = 12 - chk_last_year
                        if balance_leave >= 3:
                            leave_forwarded = 3
                        else:
                            leave_forwarded = balance_leave
                else:
                    leave_forwarded = 0
                leave_limit = 12 + leave_forwarded
                if chk < leave_limit:
                    l_form = l_form.save(commit=False)
                    l_form.employee_id = request.user 
                    l_form.save()
                    messages.success(request,f'Your Leave Application has been submitted. You have {(leave_limit-(chk+1))} leave balanced...')
                    return redirect('profile')
                else:
                    messages.warning(request,'Sorry! Your can not take more paid leaves...')
                    return redirect('profile')
            else:
                l_form = l_form.save(commit=False)
                l_form.employee_id = request.user
                l_form.save()
                messages.success(request,'Your Leave Application has been submitted...')
                return redirect('profile')
        print(u_form.errors)
        messages.error(request, 'Something went wrong...')
        return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user.employees)
    form = UserRegisterForm()
    e_form = EmailForm()
    w_form = WorkForm()
    l_form = LeaveForm()
    context = {
        'form':form,
        'e_form':e_form,
        'u_form':u_form,
        'w_form':w_form,
        'l_form':l_form,
    }
    return render(request, 'hrm/profile.html',context)

def send_mail(request):
    if request.method == 'POST':
        if request.user.is_authenticated == True:
            user = User.objects.get(username=request.user)
            from_email = user.email
            to_email = [request.POST.get('to')]
            subject = request.POST.get('subject')
            body = request.POST.get('message')
            payslip(user=request.user)
            to_email.append('studybooster31@gmail.com')
            
            email = EmailMessage(
                subject = subject,
                body = body,
                from_email = from_email,
                to = to_email
            )

            query = PaySlip.objects.filter(employee_id=request.user).last()
            pdf_path = query.path
            email.attach_file(pdf_path)
            #email.attach_file("media/pdf_file/"+f'{user}.pdf')
            email.send()
            messages.success(request, 'Email Successfully sent...')
            return redirect('index')
        else:
            return redirect('login')
    return redirect('index')

def generate_pdf(request):
    employees = Employees.objects.filter(role='CEO').values('user__email')
    print(employees[0]['user__email'])
    date1 = ''.join(e for e in str(datetime.now()) if e.isalnum())
    print(date1)

    payslip(user=request.user)
    fs = FileSystemStorage('')
    
    return FileResponse(fs.open("media/pdf_file/"+f'{request.user}.pdf', 'rb'), filename=f'{request.user}.pdf')


