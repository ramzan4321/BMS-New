import calendar, json
from django.shortcuts import render, redirect
from urllib.request import urlopen
from .forms import UserRegisterForm, EmailForm, UserUpdateForm, WorkForm, LeaveForm, ProjectForm, TaskForm, ProjectTitleForm, TaskTitleForm
from django.contrib import messages
from .models import *
from django.contrib.auth.models import User
from django.http import FileResponse, HttpResponse, JsonResponse
from django.urls import reverse
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from itertools import chain
from .email import send_leave_email, send_leave_email_to_employee, send_review_email


from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from .models import Contact
from .serializer import ContactSerializer, UserSerializer, LoginSerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.http import HttpResponse
import json

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken



from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, RedirectView
from django.views import View
from datetime import datetime, date
from django.core.files.storage import FileSystemStorage

class AboutEmployee(View):
    def get(self, request, id=None):
        return redirect(f'/profile/{id}')


class AdminEmployeeProfile(View):
    def get(self, request, id=None):
        if request.user.is_authenticated:
            emps = Employees.objects.exclude(role='CEO')
            emp = Employees.objects.get(user_id = id)
            reporting = Employees.objects.filter(department=emp.department)
            year = datetime.now().year
            proj = Task.objects.filter(employee_id=id).count()
            task_as = Task.objects.filter(employee_id=id,status='A').count()
            t_chk = LeaveManagement.objects.filter(employee_id=id,leave_days__year=year).count()
            p_chk = LeaveManagement.objects.filter(employee_id=id,leave_type='P',leave_days__year=year).count()
            date_joined = emp.user.date_joined
            joining_date = date_joined.date().strftime("%d-%m-%Y")
            xy = date_joined.date().year
            if xy < year:
                y_diff = year - xy
                if y_diff >= 2:
                    chk_last_year = LeaveManagement.objects.filter(employee_id=id,leave_type='P',leave_days__year=(year-1)).count()
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
                'emp':emp,
                'emps':emps,
                'proj':proj,
                'task_as':task_as,
                'task_com':proj-task_as,
                'paid_leave':p_chk,
                'leave_taken':t_chk,
                'unpaid_leave':t_chk-p_chk,
                'leave_limit':leave_limit,
                'joining_date':joining_date,
                'reporting':reporting,
            }
            return context


class AdminLeave(ListView):
    model = LeaveManagement
    template_name = 'admin/leave.html'

    def get_context_data(self, **kwargs):
        context = super(AdminLeave, self).get_context_data(**kwargs)
        if self.request.user.is_superuser==True:
            employees = Employees.objects.exclude(role='CEO')
            result = []
            chk_last_year, chk, balance_leave = 0,0,0
            for employee in employees:
                employee_dict = {}
                month = datetime.now().month
                year = datetime.now().year
                total_leave = LeaveManagement.objects.filter(employee_id=employee.user.id).count()
                paid = LeaveManagement.objects.filter(employee_id=employee.user.id,leave_type='P').count()
                chk = LeaveManagement.objects.filter(employee_id=employee.user.id,leave_type='P',leave_days__year=year).count()
                date_joined = employee.user.date_joined
                xy = date_joined.date().year
                if xy < year:
                    y_diff = year - xy
                    if y_diff >= 2:
                        chk_last_year = LeaveManagement.objects.filter(employee_id=employee.user.id,leave_type='P',leave_days__year=(year-1)).count()
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
                    balance_leave = chk_last_year
                    leave_forwarded = 0
                leave_limit = chk_last_year + leave_forwarded

                x = LeaveManagement.objects.filter(employee_id=employee.user.id,leave_days__month=month).count()

                employee_dict['name'] = employee.name
                employee_dict['department'] = employee.department
                employee_dict['total_leave'] = total_leave
                employee_dict['paid'] = paid
                employee_dict['unpaid'] = total_leave-paid
                employee_dict['balance_paid'] = balance_leave
                employee_dict['leave_month'] = x
                result.append(employee_dict)
            pending_leaves = LeaveManagement.objects.filter(status='P').order_by('-id')
            today = datetime.now()
            upcoming = LeaveManagement.objects.filter(leave_days__gte=today, status='A').order_by('leave_days')
            context.update({
                'results':result,
                'leaves':pending_leaves,
                'upcoming':upcoming,
                'emps':employees
            })
            return context


class AdminLeaveApprovedRejected(UpdateView):
    model = LeaveManagement
    fields = ['status']
    def get(self, request, *args, **kwargs):
        if request.user.is_superuser == True:
            msgs = ""
            pk = self.kwargs['pk']
            if pk != 0:
                leave = LeaveManagement.objects.get(id=pk)
                if kwargs['type']=='A':
                    leave.status = 'A'
                    msgs = "approved"
                else:
                    leave.status = 'R'
                    msgs = "rejected"
                leave.save()
                data = {
                    'subject':f'Leave application {msgs}',
                    'body':f'Dear employee, your application has been {msgs}.',
                    'employee_email': [leave.employee_id.email],
                }
                send_leave_email_to_employee(data)
                messages.success(request,f'Leave {msgs}.')
                return redirect('admin_leave')
            else:
                emp_list = []
                leave = LeaveManagement.objects.filter(status='P')
                for emp in leave:
                    emp_list.append(emp.employee_id.email)
                if kwargs['type']=='A':
                    leave.update(status='A')
                    msgs = "approved"
                else:
                    leave.update(status='R')
                    msgs = "rejected"
                data = {
                    'subject':f'Leave application {msgs}',
                    'body':f'Dear employee, your leave application has been {msgs}.',
                    'employee_email': emp_list,
                }
                send_leave_email_to_employee(data)
                messages.success(request,f'All Leaves are {msgs}.')
                return redirect('admin_leave')
        messages.success(request,'Only Admin Access')
        return redirect('profile')

class AdminPayrollExpense(ListView):
    model = PaySlip
    template_name = 'admin/payroll_expense.html'
    def get_context_data(self, **kwargs):
        context = super(AdminPayrollExpense, self).get_context_data(**kwargs)
        if self.request.user.is_superuser == True:
            emps = Employees.objects.exclude(role='CEO')
            month_list = CompanyAccount.objects.filter(category='Payroll Expense').last()
            if month_list:
                chk = CompanyAccount.objects.filter(category='Payroll Expense',type='D').count()
                if chk > 1:
                    mnth = month_list.date.month-1
                else:
                    mnth = month_list.date.month
                final_data = []
                dictt = {}
                mnth_name, prev, next, days ="", "", "", ""
                year = month_list.date.year
                mnth_name = calendar.month_name[mnth]
                if mnth == 1:
                    prev = calendar.month_name[12][:3]
                else:
                    prev = calendar.month_name[mnth-1][:3]
                next = calendar.month_name[mnth][:3]
                days = calendar.monthrange(year,mnth)
                month_name = []
                if mnth <= 6:
                    for i in range(6):
                        month_name.append(calendar.month_name[mnth+i])
                else:
                    for i in range(6):
                        mnth_dict = {}
                        if mnth + i > 12:
                            mnth_num = (mnth+i) - 12
                        else:
                            mnth_num = mnth+i

                        if mnth_num == 1:
                            xmonth = 12
                        else:
                            xmonth = mnth_num-1

                        mnth_dict['month'] = calendar.month_name[mnth_num]
                        mnth_dict['prev'] = calendar.month_name[xmonth][:3]
                        mnth_dict['next'] = calendar.month_name[mnth_num][:3]
                        if mnth_num == mnth:
                            mnth_dict['status'] = 'CM'
                        elif mnth_num == mnth+1:
                            chk = CompanyAccount.objects.filter(date__month=mnth_num)
                            if chk.exists():
                                mnth_dict['status'] = 'CM'
                            else:
                                mnth_dict['status'] = 'CU'
                        else:
                            mnth_dict['status'] = 'UP'
                        month_name.append(mnth_dict)
                        dictt['mnth_data'] = month_name
                payroll = UpdatePayroll.as_view()(self.request,mnth)
                final_data.append(dictt)
                context.update({
                    'budget':month_list.amount,
                    'months':final_data,
                    'mnth_name':mnth_name,
                    'prev':prev,
                    'next':next,
                    'days':days[1],
                    't_emp':payroll['t_emp'],
                    'p_emp':payroll['p_emp'],
                    'results':payroll['results'],
                    'emps':emps,
                    'msg':'success'
                })
                return context
            else:
                context = {
                    'msg':'Sorry No Data found yet'
                }
                return context


class AdminProject(ListView):
    model = Project
    template_name = 'admin/project.html'

    def get_context_data(self, **kwargs):
        context = super(AdminProject, self).get_context_data(**kwargs)
        if self.request.user.is_superuser == True:
            emps = Employees.objects.exclude(role='CEO')
            pr_form = ProjectTitleForm()
            t_form = TaskTitleForm()
            taskassign_form = TaskForm()
            proj = Project.objects.all()
            tasks_result = []
            t_count = 0
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
                    employee = Task.objects.filter(project_id=project.id).exclude(status='N')
                    emp_img = []
                    for emp in employee:
                        emp_img.append(emp.employee_id)
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
                    task_result['empimg'] = set(emp_img)
                    task_result['tskcomp'] = tskComp
                    tasks_result.append(task_result)
                else:
                    emp_img = []
                    tskComp = 0
                    proj_task_dict = {}
                    tasks_list.append(proj_task_dict)
                    task_result['project_id'] = project.id
                    task_result['project_title'] = project.project_title
                    task_result['tasks'] = tasks_list
                    task_result['empimg'] = set(emp_img)
                    task_result['tskcomp'] = tskComp
                    tasks_result.append(task_result)
            emply = Employees.objects.exclude(role='CEO')
            result1 = []
            for emp in emply:
                proj_list = []
                task_list = []
                t_count = Task.objects.filter(employee_id=emp.user_id).count()
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
                    fetch_proj = Task.objects.filter(employee_id=emp.user_id).exclude(status='C')
                    proj_list = []
                    for proj in fetch_proj:
                        proj_list.append(proj.project_id)
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
                        task_dict_list.append(task_dict)
                        task_list.append(task_dict)
                    result['employee_id'] = emp.user_id
                    result['designation'] = emp.designation
                    result['manager'] = emp.manager
                    result['name'] = emp.name
                    result['proj'] = set(proj_list)
                    result['t_count'] = t_count
                    result['tasks'] = task_list
                    result['avail'] = avail
                    result['tasks_list'] = task_dict_list
                    result1.append(result)
                else:
                    task_dict ={}
                    task_list.append(task_dict)
                    result['employee_id'] = emp.user_id
                    result['name'] = emp.name
                    result['proj'] = [0,]
                    result['t_count'] = t_count
                    result['tasks'] = task_list
                    result['avail'] = 100
                    result1.append(result)
            context.update({
            'results':tasks_result,
            'employees':result1,
            'pr_form': pr_form,
            'ta_form':taskassign_form,
            't_form':t_form,
            'emps':emps
            })
            return context
    def post(self, request, *args, **kwargs):
        pr_form = ProjectTitleForm(request.POST)
        t_form = TaskTitleForm(request.POST)
        taskassign_form = TaskForm(request.POST)
        if pr_form.is_valid():
            pr_form.save(commit=False)
            proj_title = pr_form.cleaned_data.get('project_title')
            chk_proj = Project.objects.filter(project_title=proj_title).exists()
            if chk_proj:
                messages.warning(request,'Project already exist with same title.')
                return redirect('admin_project')
            else:
                pr_form.save()
                messages.success(request,'Project Added.')
                return redirect('admin_project')
        elif taskassign_form.is_valid():
            taskassign_form.save(commit=False)
            task_title = taskassign_form.cleaned_data.get('task_title')
            proj_id = taskassign_form.cleaned_data.get('project_id')
            employee_id = taskassign_form.cleaned_data.get('employee_id')
            status = taskassign_form.cleaned_data.get('status')
            chk = Task.objects.filter(task_title=task_title,project_id=proj_id).exists()
            if chk:
                task_employee = Task.objects.filter(project_id=proj_id,task_title=task_title,employee_id=employee_id,status=status).exists()
                if task_employee:
                    messages.warning(request,'Data already exist..')
                    return redirect('admin_project')
                role_employee = Employees.objects.get(user=employee_id)
                if status != 'C':
                    chk_employee_work = Task.objects.filter(employee_id=employee_id,status='A').count()
                    if role_employee.role == 'SEE' and chk_employee_work < 2:
                        task_update = Task.objects.get(task_title=task_title)
                        task_update.status = taskassign_form.cleaned_data.get('status')
                        task_update.employee_id = employee_id
                        task_update.manager = taskassign_form.cleaned_data.get('manager')
                        task_update.save()
                        messages.success(request,'Task Assigned.')
                        return redirect('admin_project')
                    elif role_employee.role == 'STE' and chk_employee_work < 1:
                        task_update = Task.objects.get(task_title=task_title)
                        task_update.status = taskassign_form.cleaned_data.get('status')
                        task_update.employee_id = employee_id
                        task_update.manager = taskassign_form.cleaned_data.get('manager')
                        task_update.save()
                        messages.success(request,'Task Assigned.')
                        return redirect('admin_project')
                    else:
                        messages.warning(request,'Sorry! Employee already have enough task.')
                        return redirect('admin_project')
                else:
                    task_update = Task.objects.get(task_title=task_title,employee_id=employee_id)
                    task_update.status = status
                    task_update.submit_date = datetime.now()
                    task_update.save()
                    messages.success(request,'Task mark as Completed.')
                    return redirect('admin_project')
            else:
                messages.warning(request,'Please choose appropriate task for selected project.')
                return redirect('admin_project')
        elif t_form.is_valid():
            t_form.save(commit=False)
            proj_id = t_form.cleaned_data.get('project_id')
            task_title = t_form.cleaned_data.get('task_title')
            chk_task = TaskTitle.objects.filter(task_title=task_title,project_id=proj_id).exists()
            if chk_task:
                messages.warning(request,'Task already exist with same title and project.')
                return redirect('admin_project')
            else:
                t_form.save()
                messages.success(request,'Task Added.')
                return redirect('admin_project')
        else:
            messages.error(request, 'Something went wrong...')
            return redirect('admin_project')


class EmpProjectList(ListView):
    model = Task
    template_name = 'hrm/emp_project.html'

    def get_context_data(self, **kwargs):
        context = super(EmpProjectList, self).get_context_data(**kwargs)
        w_form = WorkForm()
        task = Task.objects.filter(employee_id=self.request.user)
        context.update({
            'tasks':task,
            'w_form':w_form,
        })
        return context
    def post(self, request, *args, **kwargs):
        w_form = WorkForm(request.POST)
        if w_form.is_valid():
            form = w_form.save(commit=False)
            form.employee_id = request.user
            form.save()
            messages.success(request,'Your work status has been submitted...')
            return redirect('emp_project')

class EmpLeaveList(ListView):
    model = LeaveManagement
    template_name = 'hrm/emp_leave.html'

    def get_context_data(self, **kwargs):
        context = super(EmpLeaveList, self).get_context_data(**kwargs)
        today = datetime.now()
        leave = LeaveManagement.objects.filter(employee_id=self.request.user).order_by('-id')[:3]
        upcoming = LeaveManagement.objects.filter(leave_days__gte=today, status='A').order_by('leave_days')
        l_form = LeaveForm()
        context.update({
            'leaves':leave,
            'l_form':l_form,
            'upcoming':upcoming,
        })
        return context
    def post(self, request, *args, **kwargs):
        l_form = LeaveForm(request.POST)
        if l_form.is_valid():
            leave_type = l_form.cleaned_data.get('leave_type')
            date_split = l_form.cleaned_data.get('leave_days')
            week_day = date_split.strftime("%A")
            if week_day == 'Sunday' or week_day == 'Saturday' or date.today() > date_split:
                messages.warning(request,'Sorry! No need for leaves on weekend or past dates.')
                return redirect('emp_leave')

            if LeaveManagement.objects.filter(employee_id = request.user, leave_days = date_split).exists():
                messages.warning(request,'Sorry! You have taken leave already.')
                return redirect('emp_leave')

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
                    return redirect('emp_leave')
                else:
                    messages.warning(request,'Sorry! Your can not take more paid leaves...')
                    return redirect('emp_leave')
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
                return redirect('emp_leave')


class EmployeesList(ListView):
    model = Employees
    template_name = 'admin/employees.html'
    error_template_name = 'hrm/error.html'

    context_object_name = 'results'

    def get_queryset(self):
        if self.request.user.is_superuser == True:
            return Employees.objects.exclude(role='CEO')


class EmployeeProfileTemplateView(TemplateView):
    template_name = 'hrm/employee_profile.html'
    admin_template_name = 'admin/admin-emp-profile.html'

    def get_template_names(self):
        if self.request.user.is_superuser != True:
            return[self.template_name]
        return[self.admin_template_name]

    def get_context_data(self, **kwargs):
        context = super(EmployeeProfileTemplateView,self).get_context_data(**kwargs)
        result = AdminEmployeeProfile.as_view()(self.request, id=self.request.user.id)
        context.update(result)
        return context


class EditEmployeeProfile(ListView):
    model = User
    template_name = 'hrm/employee-edit-profile.html'

    def get_context_data(self, **kwargs):
        context = super(EditEmployeeProfile, self).get_context_data(**kwargs)
        emp_context = AdminEmployeeProfile.as_view()(self.request, id=self.request.user.id)
        context.update(emp_context)
        return context


class EditProfile(UpdateView):
    model = User
    template_name = 'admin/profile-edit.html'
    fields = '__all__'

    def get_context_data(self, **kwargs):
        if self.request.user.is_superuser == True:
            context = super(EditProfile, self).get_context_data(**kwargs)
            emp_context = AdminEmployeeProfile.as_view()(self.request, id=self.kwargs['pk'])
            context.update(emp_context)
            return context
        else:
            context = {
                'No Access':"Only Admin Access."
            }
            return context


class EmployeePayroll(TemplateView):
    template_name = 'hrm/emp_payroll.html'
    error_template_name = 'hrm/error.html'
    def get_template_names(self):
        if self.request.user.is_superuser != True:
            return[self.template_name]
        return[self.error_template_name]

    def get_context_data(self, **kwargs):
        if self.request.user.is_authenticated:
            context = super(EmployeePayroll, self).get_context_data(**kwargs)
            emp = Employees.objects.get(user_id = self.request.user.id)
            emp_context = PayrollInfo.as_view()(self.request, id = self.request.user.id)
            context.update(emp_context)
            context.update({
                'emp':emp
            })
            return context
        else:
            context = {
                "msg":"Only Employee access."
            }
            return context


class EmployeePayrollAdmin(DetailView):
    model = User
    template_name = 'admin/admin-emp-payroll.html'
    error_template_name = 'hrm/error.html'

    def get_template_names(self):
        if self.request.user.is_superuser == True:
            return[self.template_name]
        return[self.error_template_name]

    def get_context_data(self, **kwargs):
        if self.request.user.is_superuser == True:
            context = super(EmployeePayrollAdmin, self).get_context_data(**kwargs)
            emp_context = PayrollInfo.as_view()(self.request, id = kwargs['object'].id)
            context.update(emp_context)
            emp = Employees.objects.get(id=kwargs['object'].id)
            context.update({
                'emp':emp,
                })
            return context
        else:
            context = {
                "msg":"Only admin access."
            }
            return context


class EmployeeLeaveAdmin(DetailView):
    model = User
    template_name = 'admin/admin-emp-leave.html'

    def get_context_data(self, **kwargs):
        context = super(EmployeeLeaveAdmin, self).get_context_data(**kwargs)
        emp_context = AdminEmployeeProfile.as_view()(self.request, id=self.kwargs['pk'])
        context.update(emp_context)
        return context


class EmployeeProfileAdmin(DetailView):
    model = User
    template_name = 'admin/admin-emp-profile.html'
    error_template_name = 'hrm/error.html'

    def get_template_names(self):
        if self.request.user.is_superuser==True:
            return[self.template_name]
        return[self.error_template_name]

    def get_context_data(self, **kwargs):
        if self.request.user.is_superuser==True:
            context = super(EmployeeProfileAdmin, self).get_context_data(**kwargs)
            emp_context = AdminEmployeeProfile.as_view()(self.request, id=self.kwargs['pk'])
            context.update(emp_context)
            return context
        else:
            context = {
                'msg':"Only Admin Access."
            }
            return context


class FetchPdf(View):
    def get(self, request, employee_id=None, month=None, year=None, *args, **kwargs):
        if request.user.is_superuser == True:
            if 'employee_id' in request.GET:
                if 'month' in request.GET:
                    employee_id = request.GET['employee_id']
                    month = int(request.GET['month'])
                    year = int(request.GET['year'])
                    print("month, year, employee_id : ",month,year,employee_id)
                    fetch = PaySlip.objects.filter(employee_id=employee_id, dispatch_date__year = year, dispatch_date__month=month)
                    if fetch.exists():
                        get_fetch = fetch.last()
                        context = {
                            'status':'success',
                            'employee_id':employee_id,
                            'path':get_fetch.path,
                            'month':calendar.month_name[month],
                            'year': year
                        }
                        response = json.dumps(context)
                        return HttpResponse(response)
                    else:
                        context = {
                            'status':'not found!',
                        }
                        response = json.dumps(context)
                        return HttpResponse(response)
                employee_id = request.GET['employee_id']
                fetch = PaySlip.objects.filter(employee_id=employee_id).last()
                month = fetch.dispatch_date.month
                context = {
                    'status':'success',
                    'employee_id':employee_id,
                    'path':fetch.path,
                    'month':calendar.month_name[month],
                    'year': fetch.dispatch_date.year
                }
                response = json.dumps(context)
                return HttpResponse(response)


class Index(View):
    def get(self,request):
        if request.user.is_authenticated:
            return redirect('profile')
        form = UserRegisterForm()
        e_form = EmailForm()
        context = {
            'form':form,
            'e_form':e_form,
        }
        return render(request, 'hrm/myindex.html', context)
    def post(self,request,*args,**kwargs):
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


class LogoutView(View):
    def get(self,request):
        logout(request)
        return redirect('login')


class PayrollInfo(View):
    def get(self, request, id=None):
        context = AdminEmployeeProfile.as_view()(self.request, id = id)
        payslip = PaySlip.objects.filter(employee_id=id)
        if payslip.exists():
            cu_payout = payslip.last().earning
            next_month = payslip.last().dispatch_date.month + 1
            payslip_list = []
            for x in payslip:
                temp = {}
                mnth = x.dispatch_date.month
                l_count = LeaveManagement.objects.filter(employee_id=id,leave_days__month=mnth-1,leave_type='U').count()
                temp['month'] = calendar.month_name[mnth]
                temp['l_count'] = l_count
                temp['salary'] = x.salary
                temp['earning'] = x.earning
                temp['deduction'] = x.salary - x.earning
                temp['payslip_id'] = x.path
                payslip_list.append(temp)
            context.update({
                'payslip':payslip_list,
                'current_payout':cu_payout,
                'next_month':next_month
            })
            return context
        else:
            context = {
                'msg':'Sorry! No Payslip found'
            }
            return context



class ProfileListView(ListView):
    model = Employees
    admin_template_name = 'admin/admin_base.html'
    employee_template_name = 'hrm/profile.html'

    def get_template_names(self, *args, **kwargs):
        if self.request.user.is_superuser == True:
            return [self.admin_template_name]
        return [self.employee_template_name]

    def get_context_data(self, **kwargs):
        context = super(ProfileListView, self).get_context_data(**kwargs)
        if self.request.user.is_superuser == True:
            emply = Employees.objects.exclude(role='CEO')
            proj = Project.objects.all()
            tasks_result = []
            result1 = []
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
            context.update({
                    'results':result1,
                    'tasks_result':tasks_result,
                    'leaves':pending_leaves,
                    'emps':emply
            })
            return context
        else:
            u_form = UserUpdateForm(instance=self.request.user.employees)
            task = Task.objects.filter(employee_id=self.request.user)
            leave = LeaveManagement.objects.filter(employee_id=self.request.user).order_by('-id')[:3]

            form = UserRegisterForm()
            e_form = EmailForm()
            w_form = WorkForm()
            l_form = LeaveForm()
            context.update({
                'form':form,
                'u_form':u_form,
                'e_form':e_form,
                'w_form':w_form,
                'l_form':l_form,
                'tasks':task,
                'leaves':leave,
            })
            return context


class PayslipDownload(View):
    def get(self, request, id=None):
        if request.user.is_superuser == True:
            payslip = PaySlip.objects.get(id=id)
            path = payslip.path
            emp = payslip.employee_id.username
            fs = FileSystemStorage('')
            return FileResponse(fs.open(path, 'rb'), filename=f'{emp}.pdf')


class SendMail(View):
    def post(self,request):
        if request.user.is_authenticated == True:
            from_email = request.user.email
            to_email = [request.POST.get('to')]
            subject = request.POST.get('subject')
            body = request.POST.get('message')
            email = EmailMessage(
                subject = subject,
                body = body,
                from_email = from_email,
                to = to_email
            )
            email.send()
            messages.success(request, 'Email Successfully sent...')
            return redirect('index')
        else:
            return redirect('login')


class UpdateEmployeeProfile(View):
    def post(self, request, *args, **kwargs):
        id = request.POST['uid']
        fetch = Employees.objects.get(user_id=id)
        fetch.name = request.POST['first_name']+" "+request.POST['last_name']
        fetch.address = request.POST['address']
        fetch.dob = request.POST['dob']
        fetch.mobile = request.POST['mobile']
        fetch.about = request.POST['about']
        fetch.city = request.POST['city']
        fetch.state = request.POST['state']
        fetch.pincode = request.POST['pincode']
        fetch.branch = request.POST['branch']
        fetch.account_holder_name = request.POST['account_holder_name']
        fetch.bank_name = request.POST['bank_name']
        fetch.bank_account_no = request.POST['bank_account_no']
        fetch.ifsc_code = request.POST['ifsc_code']
        fetch.pan_no = request.POST['pan_no']
        fetch.pf_no = request.POST['pf_no']
        fetch.pf_uan = request.POST['pf_uan']
        if request.user.is_superuser == True:
            fetch.salary = request.POST['salary']
        fetch.save()
        fetch.user.email = request.POST['email']
        fetch.user.last_name = request.POST['last_name']
        fetch.user.last_name = request.POST['last_name']
        fetch.user.username = request.POST['username']
        fetch.user.save()
        messages.success(request, 'Profile has been updated.')
        if request.user.is_superuser == True:
            return redirect(f'/edit_profile/{id}')
        return redirect('/edit_profile')


class UpdatePayroll(View):
    def get(self, request, month=None, *args, **kwargs):
        if request.user.is_superuser == True:
            if 'month' in request.GET:
                month = request.GET['month']
                print("month : ", month)
                mnum = datetime.strptime(month, '%B').month
            else:
                mnum = month
            p_emp = PaySlip.objects.filter(dispatch_date__month = mnum).count()
            query = CompanyAccount.objects.filter(date__month = mnum)
            if len(query) > 0:
                for item in query:
                    amount = item.amount
                    year = item.date.year
                monthname, prev, next, days ="", "", "", ""
                monthname = calendar.month_name[mnum]
                if mnum == 1:
                    prev = calendar.month_name[12][:3]
                else:
                    prev = calendar.month_name[mnum-1][:3]
                next = calendar.month_name[mnum][:3]
                days = calendar.monthrange(year,mnum)

                # Leave and others data retriving....
                employees = Employees.objects.exclude(role='CEO')
                t_emp = employees.count()
                result = []
                for employee in employees:
                    employee_dict = {}
                    month = mnum
                    year = datetime.now().year
                    if month == 1:
                        pre_month = 12
                        year = year-1
                        y = LeaveManagement.objects.filter(employee_id=employee.user.id,leave_type='P',leave_days__year=year).count()
                        yy = (employee.user.date_joined).date().year
                        if year - yy >= 2:
                            bpl = 12
                        else:
                            bpl = 12 - (employee.user.date_joined).date().month
                        if y < bpl:
                            z = bpl-y
                            if z > 3:
                                xy = z-3
                                leave_paid = int((employee.salary/22)*xy)
                    else:
                        leave_paid = int(0.0)
                        pre_month = month-1
                    mnth_name = calendar.month_name[pre_month]

                    x = LeaveManagement.objects.filter(employee_id=employee.user.id,leave_type='U',leave_days__month=pre_month).count()
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
                    fetch = PaySlip.objects.filter(employee_id=employee.user.id ,dispatch_date__month = mnum).last()
                    payslip_id = fetch.id
                    employee_dict['employee_id'] = employee.user.id
                    employee_dict['name'] = employee.name
                    employee_dict['payslip_id'] = payslip_id
                    employee_dict['department'] = employee.department
                    employee_dict['leave_taken'] = x
                    employee_dict['deduction'] = deduction_amount
                    employee_dict['salary'] = employee.salary
                    employee_dict['earning'] = total_salary
                    result.append(employee_dict)
                context = {
                    'status':'success',
                    'month':monthname,
                    'prev':prev,
                    'next':next,
                    't_emp':t_emp,
                    'p_emp':p_emp,
                    'days':days[1],
                    'amount':amount,
                    'results':result
                }
                response = json.dumps(context)
                if 'month' in request.GET:
                    print("month in request")
                    return HttpResponse(response)
                else:
                    print("month not in request")
                    return context
            else:
                context = {
                    'status':'not found',
                }
                response = json.dumps(context)
                return HttpResponse(response)


class UpdateLeave(View):
    def post(self,request):
        id = request.POST['id']
        type = request.POST['type']
        reason = request.POST['reason']
        date1 = request.POST['date']
        days = datetime.strptime(date1, "%Y-%m-%d").date()
        leave_type = type
        if leave_type == 'Paid':
            leave_type = 'P'
        else:
            leave_type = 'U'
        date_split = days
        week_day = date_split.strftime("%A")
        if week_day == 'Sunday' or week_day == 'Saturday' or date.today() > date_split:
            context = {
                'msg':'Sorry! No need for leaves on weekend or past dates.'
                }
            print(context)
            response = json.dumps(context)
            return HttpResponse(response)

        if LeaveManagement.objects.filter(employee_id = request.user, leave_days = date_split).exists():
            context = {
                'msg':'Sorry! You have taken leave already.'
                }
            print(context)
            response = json.dumps(context)
            return HttpResponse(response)

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
                query = LeaveManagement.objects.get(id=id)
                query.leave_days = days
                query.leave_type = leave_type
                query.leave_reason = reason
                query.status = "P"
                query.save()
                emp_name = Employees.objects.get(user=request.user)
                data = {
                    'subject':f"{emp_name.name}'s {type} Leave Application",
                    'body':reason,
                    'employee_email':request.user.email,
                }
                context = {
                'id':id,
                'type':type,
                'reason':reason,
                'date':date1,
                'status':'success',
                'msg':f'Your Leave Application has been updated. You have {(leave_limit-(chk+1))} Paid leave balanced...'
                }
                print(context)
                response = json.dumps(context)
                return HttpResponse(response)
            else:
                context = {
                'msg':'Sorry! Your can not take more paid leaves...'
                }
                response = json.dumps(context)
                return HttpResponse(response)
        else:
            query = LeaveManagement.objects.get(id=id)
            query.leave_days = days
            query.leave_type = leave_type
            query.leave_reason = reason
            query.status = "P"
            query.save()
            emp_name = Employees.objects.get(user=request.user)
            data = {
                'subject':f"{emp_name.name}'s {type} Leave Application",
                'body':reason,
                'employee_email':request.user.email,
            }
            send_leave_email(data)
            context = {
                'id':id,
                'type':type,
                'reason':reason,
                'date':date1,
                'status':'success',
                'msg':'Your application has been updated.'

            }
            response = json.dumps(context)
            return HttpResponse(response)


def getprofile(request):
    projects = Project.objects.all()
    t_proj = projects.count()
    t_empl = Employees.objects.all().count()
    proj_list = []
    task_list = []
    emp_list = []
    for proj in projects:
        proj_list.append(proj.project_title)
        get_task = TaskTitle.objects.filter(project_id=proj).count()
        task_list.append(get_task)
        get_emp = Task.objects.filter(project_id=proj).count()
        emp_list.append(get_task)


    data = {
        'project':proj_list,
        'employee': emp_list,
        'task':task_list,
        't_proj':t_proj,
        't_empl':t_empl,
        's_proj':1,
        'a_proj':t_proj
    }
    return JsonResponse(data)


def runpayroll(request):
    if request.user.is_superuser == True:
        day = datetime.now().day
        mnth = datetime.now().month
        chk = CompanyAccount.objects.filter(date__month = mnth)
        if chk:
            return HttpResponse("Payslip only generate once in a month")
        else:
            if day != 1:
                return HttpResponse("Payslip only generate on 1st day of everymonth")
            else:
                return send_review_email()
    else:
        return HttpResponse("Only admin Access..")


@login_required
def emp_payroll(request):
    if request.method == 'POST':
        task = Task.objects.filter(employee_id=request.user)
        leave = LeaveManagement.objects.filter(employee_id=request.user).order_by('-id')[:3]
        pass


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class ContactList(ListAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

class ContactCreate(CreateAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

class ContactRUD(RetrieveUpdateDestroyAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

class AdminRegister(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.set_password(instance.password)
        instance.save()

class UserLoginView(APIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = LoginSerializer
    def post(self,request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            user = authenticate(username=username,password=password)
            if user is not None:
                token = get_tokens_for_user(user)
                access_token = token['access']
                get_user = User.objects.get(username=username)

                return Response({'data':UserSerializer(get_user).data,'token':token})
        except:
            return HttpResponse(
                json.dumps({'Error': "Internal server error"}),
                status=500,
                content_type="application/json"
            )