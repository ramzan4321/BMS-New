import itertools
from django.shortcuts import render, redirect
from .forms import UserRegisterForm, EmailForm, UserUpdateForm, WorkForm, LeaveForm, ProjectForm, TaskForm, ProjectTitleForm, TaskTitleForm
from django.contrib import messages
from .models import Employees, EmployeesWorkDetails,LeaveManagement, PaySlip, Project, Task, TaskTitle
from django.contrib.auth.models import User
from django.http import FileResponse, HttpResponseRedirect
from django.urls import reverse
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from itertools import chain
from .email import send_leave_email, send_leave_email_to_employee

from datetime import datetime, date
from django.core.files.storage import FileSystemStorage
from django.utils import timezone    
from .payslip_pdf import generate_pdf as payslip


def index(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=raw_password)
            if user is not None:
                login(request, user)
            messages.success(request,f'{username}! Welcome to Triodec...')
            return redirect('index')
        print(form.errors)
    elif request.user.is_authenticated:
        return redirect('profile')
    form = UserRegisterForm()
    e_form = EmailForm()
    context = {
        'form':form,
        'e_form':e_form,
    }
    return render(request, 'hrm/index.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, request.FILES, instance=request.user.employees)
        w_form = WorkForm(request.POST)
        l_form = LeaveForm(request.POST)
        pr_form = ProjectTitleForm(request.POST)
        t_form = TaskTitleForm(request.POST)
        taskassign_form = TaskForm(request.POST)
        if u_form.is_valid():
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
            week_day = date_split.strftime("%A")
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
                xy = date_joined.date().year
                if xy < year:
                    y_diff = year - xy
                    if y_diff >= 2:
                        chk_last_year = LeaveManagement.objects.filter(employee_id=request.user,leave_type='P',leave_days__year=(year-1)).count()
                    else:
                        chk_last_year = 12 - date_joined.date().month
                    if chk_last_year < 12:
                        balance_leave = 12 - chk_last_year
                        if balance_leave >= 3:
                            leave_forwarded = 3
                        else:
                            leave_forwarded = balance_leave
                else:
                    chk_last_year = 12 - date_joined.date().month
                    leave_forwarded = 0
                leave_limit = chk_last_year + leave_forwarded
                if chk < leave_limit:
                    l_form = l_form.save(commit=False)
                    l_form.employee_id = request.user
                    leave_reason = l_form.leave_reason 
                    l_form.save()
                    emp_name = Employees.objects.get(user=request.user)
                    data = {
                        'subject':f"{emp_name.name}'s Leave Application",
                        'body':leave_reason,
                        'employee_email':request.user.email,
                    }
                    messages.success(request,f'Your Leave Application has been submitted. You have {(leave_limit-(chk+1))} Paid leave balanced...')
                    return redirect('profile')
                else:
                    messages.warning(request,'Sorry! Your can not take more paid leaves...')
                    return redirect('profile')
            else:
                l_form = l_form.save(commit=False)
                l_form.employee_id = request.user
                leave_reason = l_form.leave_reason
                l_form.save()
                emp_name = Employees.objects.get(user=request.user)
                data = {
                    'subject':f"{emp_name.name}'s Leave Application",
                    'body':leave_reason,
                    'employee_email':request.user.email,
                }
                send_leave_email(data)
                messages.success(request,'Your Leave Application has been submitted...')
                return redirect('profile')
        elif pr_form.is_valid():
            pr_form.save(commit=False)
            proj_title = pr_form.cleaned_data.get('project_title')
            chk_proj = Project.objects.filter(project_title=proj_title).exists()
            if chk_proj:
                messages.warning(request,'Project already exist with same title.')
                return redirect('profile')
            else:
                pr_form.save()
                messages.success(request,'Project Added.')
                return redirect('profile')
        elif taskassign_form.is_valid():
            taskassign_form.save(commit=False)
            task_title = taskassign_form.cleaned_data.get('task_title')
            proj_id = taskassign_form.cleaned_data.get('project_id')
            employee_id = taskassign_form.cleaned_data.get('employee_id')
            chk = Task.objects.filter(task_title=task_title,project_id=proj_id).exists()
            if chk:
                task_employee = Task.objects.filter(project_id=proj_id,task_title=task_title,employee_id=employee_id).exists()
                if task_employee:
                    messages.warning(request,'Data already exist..')
                    return redirect('profile')
                role_employee = Employees.objects.get(user=employee_id)
                chk_employee_work = Task.objects.filter(employee_id=employee_id,status='A').count() 
                if role_employee.role == 'SEE' and chk_employee_work < 2:
                    task_update = Task.objects.get(task_title=task_title)
                    task_update.status = taskassign_form.cleaned_data.get('status')
                    task_update.employee_id = employee_id
                    task_update.manager = taskassign_form.cleaned_data.get('manager')
                    task_update.save()
                    messages.success(request,'Task Assigned.')
                    return redirect('profile')
                elif role_employee.role == 'STE' and chk_employee_work < 1:
                    task_update = Task.objects.get(task_title=task_title)
                    task_update.status = taskassign_form.cleaned_data.get('status')
                    task_update.employee_id = employee_id
                    task_update.manager = taskassign_form.cleaned_data.get('manager')
                    task_update.save()
                    messages.success(request,'Task Assigned.')
                    return redirect('profile')
                else:
                    messages.warning(request,'Sorry! Employee already have enough task.')
                    return redirect('profile')
            else:
                taskassign_form.save()
                messages.success(request,'Task Assigned.')
                return redirect('profile')
        elif t_form.is_valid():
            t_form.save(commit=False)
            proj_id = t_form.cleaned_data.get('project_id')
            task_title = t_form.cleaned_data.get('task_title')
            chk_task = TaskTitle.objects.filter(task_title=task_title,project_id=proj_id).exists()
            if chk_task:
                messages.warning(request,'Task already exist with same title and project.')
                return redirect('profile')
            else:
                t_form.save()
                messages.success(request,'Task Added.')
                return redirect('profile')
        else:
            messages.error(request, 'Something went wrong...')
            return redirect('profile')
    else:
        if request.user.is_superuser == False:
            u_form = UserUpdateForm(instance=request.user.employees)
        else:
            pr_form = ProjectTitleForm()
            t_form = TaskTitleForm()
            taskassign_form = TaskForm()
            emply = Employees.objects.exclude(role='CEO')
            proj = Project.objects.all()
            tasks_result = []
            for project in proj:
                tasks_list = []
                total_count = TaskTitle.objects.filter(project_id=project.id).count()
                c_count = Task.objects.filter(project_id=project.id, status='C').count()
                if c_count != 0:
                    tskComp = int((100/total_count)*c_count)
                else:
                    tskComp = 0
                task_check = Task.objects.filter(project_id=project.id).exists()
                task_result = {}
                if task_check:
                    qs1 = Task.objects.filter(project_id=project.id,status='C')
                    qs2 = Task.objects.filter(project_id=project.id,status='A').exclude(status='C')
                    qs3 = Task.objects.filter(project_id=project.id,status='N').exclude(status='A')
                    
                    proj_task = chain(qs1,qs2,qs3)
                    for tsk in proj_task:
                        proj_task_dict = {}
                        proj_task_dict['id'] = tsk.id
                        proj_task_dict['task_title'] = tsk.task_title
                        proj_task_dict['status'] = tsk.status
                        tasks_list.append(proj_task_dict)
                    task_result['project_id'] = project.id
                    task_result['project_title'] = project.project_title
                    task_result['tasks'] = tasks_list
                    task_result['tskcomp'] = tskComp
                    tasks_result.append(task_result)
                else:
                    tskComp = 0
                    proj_task_dict = {}
                    tasks_list.append(proj_task_dict)
                    task_result['project_id'] = project.id
                    task_result['project_title'] = project.project_title
                    task_result['tasks'] = tasks_list
                    task_result['tskcomp'] = tskComp
                    tasks_result.append(task_result)

                result1 = []
                for emp in emply:
                    task_list = []
                    check = Task.objects.filter(employee_id=emp.user_id).exclude(status='C').exists()
                    count = Task.objects.filter(employee_id=emp.user_id).exclude(status='C').count()
                    result = {}
                    if check:
                        if emp.role == 'SEE' and count > 1:
                            avail = 0
                        else:
                            avail = 50
                        if emp.role == 'STE':
                            avail = 0
                        fetch_task = Task.objects.filter(employee_id=emp.user_id).exclude(status='C')
                        task_dict_list = []
                        for task in fetch_task:
                            task_dict ={}
                            task_dict['id'] = task.id
                            task_dict['project_id'] = task.project_id
                            task_dict['task_title'] = task.task_title
                            task_dict['manager'] = task.manager
                            task_dict['employee_id'] = task.employee_id
                            task_dict['start_date'] = task.start_date
                            task_dict['status'] = task.status
                            task_dict['avail'] = avail
                            task_dict_list.append(task_dict)
                            task_list.append(task_dict)
                        result['employee_id'] = emp.user_id
                        result['designation'] = emp.designation
                        result['manager'] = emp.manager
                        result['name'] = emp.name
                        result['tasks'] = task_list
                        result['tasks_list'] = task_dict_list
                        result1.append(result)
                    else:
                        task_dict ={}
                        task_list.append(task_dict)
                        result['employee_id'] = emp.user_id
                        result['name'] = emp.name
                        result['tasks'] = task_list
                        result1.append(result)
            pending_leaves = LeaveManagement.objects.filter(status='P').order_by('-id')
            context = {
                'results':result1,
                'pr_form': pr_form,
                'ta_form':taskassign_form,
                't_form':t_form,
                'tasks_result':tasks_result,
                'leaves':pending_leaves
            }
            return render(request, 'hrm/admin_dashboard.html', context)
            #return HttpResponseRedirect(reverse('admin:index'))
        
        task = Task.objects.filter(employee_id=request.user)
        leave = LeaveManagement.objects.filter(employee_id=request.user).order_by('-id')[:3]

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
        'tasks':task,
        'leaves':leave,
    }
    return render(request, 'hrm/profile.html',context)

def send_mail(request):
    if request.method == 'POST':
        if request.user.is_authenticated == True:
            from_email = request.user.email
            to_email = [request.POST.get('to')]
            subject = request.POST.get('subject')
            body = request.POST.get('message')
            payslip(user=request.user)
            email = EmailMessage(
                subject = subject,
                body = body,
                from_email = from_email,
                to = to_email
            )

            query = PaySlip.objects.filter(employee_id=request.user).last()
            pdf_path = query.path
            email.attach_file(pdf_path)
            email.send()
            messages.success(request, 'Email Successfully sent...')
            return redirect('index')
        else:
            return redirect('login')
    return redirect('index')


def employee_profile_admin(request, user_id):
    if request.user.is_superuser == True:
        result = Employees.objects.get(user_id=user_id)
        year = datetime.now().year
        chk = LeaveManagement.objects.filter(employee_id=result.id,leave_type='P',leave_days__year=year).count()
        date_joined = result.user.date_joined
        joining_date = date_joined.date().strftime("%d %B %Y")
        xy = date_joined.date().year
        if xy < year:
            y_diff = year - xy
            if y_diff >= 2:
                chk_last_year = LeaveManagement.objects.filter(employee_id=result.id,leave_type='P',leave_days__year=(year-1)).count()
            else:
                chk_last_year = 12 - date_joined.date().month
            if chk_last_year < 12:
                balance_leave = 12 - chk_last_year
                if balance_leave >= 3:
                    leave_forwarded = 3
                else:
                    leave_forwarded = balance_leave
        else:
            chk_last_year = 12 - date_joined.date().month
            leave_forwarded = 0
        leave_limit = chk_last_year + leave_forwarded

        context = {
            'result':result,
            'leave_taken':chk,
            'leave_left':leave_limit-chk,
            'leave_limit':leave_limit,
            'joining_date':joining_date,
            'dob': result.dob.strftime("%d %B %Y"),
        }
        return render(request, 'hrm/employee_profile.html', context)

def employee_profile(request):
    if request.user.is_authenticated == True:
        result = Employees.objects.get(user=request.user)

        year = datetime.now().year
        chk = LeaveManagement.objects.filter(employee_id=request.user,leave_type='P',leave_days__year=year).count()
        date_joined = result.user.date_joined
        joining_date = date_joined.date().strftime("%d %B %Y")
        xy = date_joined.date().year
        if xy < year:
            y_diff = year - xy
            if y_diff >= 2:
                chk_last_year = LeaveManagement.objects.filter(employee_id=request.user,leave_type='P',leave_days__year=(year-1)).count()
            else:
                chk_last_year = 12 - date_joined.date().month
            if chk_last_year < 12:
                balance_leave = 12 - chk_last_year
                if balance_leave >= 3:
                    leave_forwarded = 3
                else:
                    leave_forwarded = balance_leave
        else:
            chk_last_year = 12 - date_joined.date().month
            leave_forwarded = 0
        leave_limit = chk_last_year + leave_forwarded

        context = {
            'result':result,
            'leave_taken':chk,
            'leave_left':leave_limit-chk,
            'leave_limit':leave_limit,
            'joining_date':joining_date,
            'dob': result.dob.strftime("%d %B %Y"),
        }
        return render(request, 'hrm/employee_profile.html', context)


def generate_pdf(request):
    '''employees = Employees.objects.filter(role='CEO').values('user__email')
    print(employees[0]['user__email'])
    date1 = ''.join(e for e in str(datetime.now()) if e.isalnum())
    print(date1)
    p = LeaveManagement.objects.filter(employee_id=request.user,leave_type='P',leave_days__year='2022').count()
    print("Paid leaves had been taken :",p)'''
    payslip(user=request.user)
    fs = FileSystemStorage('')
    
    return FileResponse(fs.open("media/pdf_file/"+f'{request.user}.pdf', 'rb'), filename=f'{request.user}.pdf')


def leave_approved(request,pk):
    if request.user.is_superuser == True:
        if pk != 0:
            leave = LeaveManagement.objects.get(id=pk)
            leave.status = 'A'
            leave.save()
            data = {
                'subject':'Leave Application Approved',
                'body':f'Dear employee, your application has been approved.',
                'employee_email': [leave.employee_id.email],
            }
            send_leave_email_to_employee(data)
            messages.success(request,'Leave approved.')
            return redirect('profile')
        else:
            emp_list = []
            leave = LeaveManagement.objects.filter(status='P')
            for emp in leave:
                emp_list.append(emp.employee_id.email)
            leave.update(status='A')
            data = {
                'subject':'Leave Application Approved',
                'body':'Dear employee, your leave application has been approved.',
                'employee_email': emp_list,
            }
            send_leave_email_to_employee(data)
            messages.success(request,'All Leaves are approved.')
            return redirect('profile')
    messages.success(request,'Only Admin Access')
    return redirect('profile')

def leave_rejected(request,pk):
    if request.user.is_superuser == True:
        if pk != 0:
            leave = LeaveManagement.objects.get(id=pk)
            leave.status = 'R'
            leave.save()
            data = {
                'subject':'Leave Application Rejected',
                'body':'Dear employee, Sorry for the inconvenience, your application has been rejected.',
                'employee_email': [leave.employee_id.email],
            }
            send_leave_email_to_employee(data)
            messages.success(request,'Leave rejected.')
            return redirect('profile')
        else:
            emp_list = []
            leave = LeaveManagement.objects.filter(status='P')
            for emp in leave:
                emp_list.append(emp.employee_id.email)
            leave.update(status='R')
            data = {
                'subject':'Leave Application Rejected',
                'body':'Dear employee, Sorry for the inconvenience, your application has been rejected.',
                'employee_email': emp_list,
            }
            send_leave_email_to_employee(data)
            messages.success(request,'All Leaves are rejected.')
            return redirect('profile')
    messages.success(request,'Only Admin Access.')
    return redirect('profile')

