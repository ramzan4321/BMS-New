"""business_management_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from hrm import views as hrm_views
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from hrm.api import views as api_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', hrm_views.Index.as_view(), name='index'),
    path('icons/', TemplateView.as_view(template_name='home/icons.html'), name='icons'),
    path('profile/', login_required(hrm_views.ProfileListView.as_view()), name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='hrm/login.html'), name='login'),
    path('logout/', hrm_views.LogoutView.as_view(), name='logout'),
    path('employee_profile_view/', hrm_views.EmployeeProfileTemplateView.as_view() , name='employee_profile_view'),
    path('profile/<int:pk>', hrm_views.EmployeeProfileAdmin.as_view() , name='emp_profile'),
    path('employees/', hrm_views.EmployeesList.as_view() , name='employees'),
    path('edit_profile/<int:pk>', hrm_views.EditProfile.as_view() , name='edit_profile'),
    path('edit_profile/', hrm_views.EditEmployeeProfile.as_view() , name='edit_emp_profile'),
    path('about_employee/<int:id>', hrm_views.AboutEmployee.as_view() , name='about_employee'),
    path('payslip_download/<int:id>', hrm_views.PayslipDownload.as_view() , name='payslip_download'),
    path('emp_payroll/<int:pk>', hrm_views.EmployeePayrollAdmin.as_view() , name='emp_payroll_admin'),
    path('emp_payroll/', hrm_views.EmployeePayroll.as_view() , name='emp_payroll'),
    path('emp_leave/<int:pk>', hrm_views.EmployeeLeaveAdmin.as_view() , name='emp_leave'),
    path('update_emp_profile/', hrm_views.UpdateEmployeeProfile.as_view(), name='update_emp_profile'),
    path('send_mail/', hrm_views.SendMail.as_view() , name='send_mail'),
    path('payroll_expenses/', hrm_views.AdminPayrollExpense.as_view() , name='payroll_expense'),
    path('run_payroll/', hrm_views.runpayroll , name='run_payroll'),
    path('update_payroll/', hrm_views.UpdatePayroll.as_view() , name='update_payroll'),
    path('fetch_pdf/', hrm_views.FetchPdf.as_view() , name='fetch_pdf'),
    path('getprofile/', hrm_views.getprofile , name='getprofile'),
    path('logins/', TemplateView.as_view(template_name="home/login.html"), name="logins"),
    path('register/', TemplateView.as_view(template_name="home/register.html"), name="register"),
    path('tables/', TemplateView.as_view(template_name="home/tables.html"), name="tables"),
    path('project/',hrm_views.AdminProject.as_view() , name="admin_project"),
    path('leave/', hrm_views.AdminLeave.as_view(), name="admin_leave"),

    path('emp_project/',hrm_views.EmpProjectList.as_view() , name="emp_project"),
    path('emp_leave/',hrm_views.EmpLeaveList.as_view() , name="emp_leave"),
    path('emp_payroll/',hrm_views.emp_payroll , name="emp_payroll"),

    path('api/leave/', api_view.LeaveAPI.as_view() , name='employee'),

    path('leave_approved/<int:pk>/<str:type>', hrm_views.AdminLeaveApprovedRejected.as_view() , name='leaveapproved'),
    path('leave_rejected/<int:pk>/<str:type>', hrm_views.AdminLeaveApprovedRejected.as_view() , name='leaverejected'),

    path('updateleave/', hrm_views.UpdateLeave.as_view() , name='updateleave'),
    
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('contact/', hrm_views.ContactCreate.as_view()),
    path('contactlist/', hrm_views.ContactList.as_view()),
    path('contactlist/<int:pk>', hrm_views.ContactRUD.as_view()),
    path('admin_register_/', hrm_views.AdminRegister.as_view()),

    path('apilogin/', hrm_views.UserLoginView.as_view(), name='apilogin'),
    path('gettoken/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refreshtoken/', TokenRefreshView.as_view(), name='token_refresh'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
