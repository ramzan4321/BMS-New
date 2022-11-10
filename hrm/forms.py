from dataclasses import fields
from email import message
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth.models import User
from .models import Employees,EmployeesWorkDetails,LeaveManagement

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class EmailForm(forms.Form):
    to = forms.EmailField()
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)


class UserUpdateForm(forms.ModelForm):
    dob = forms.DateField(
         widget=forms.TextInput(     
        attrs={'type': 'date'} 
    )
    )
    class Meta:
        model = Employees
        exclude = ['user','salary','paid_days']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Employees
        fields = ['image'] 

class WorkForm(forms.ModelForm):
    working_day = forms.DateField(
        widget=forms.TextInput(     
        attrs={'type': 'date'} 
    )
    )
    end_day_time = forms.DateField(
        widget=forms.TextInput(     
        attrs={'type': 'datetime-local'} 
    )
    )
    class Meta:
        model = EmployeesWorkDetails
        exclude = ['employee_id']

class LeaveForm(forms.ModelForm):
    leave_days = forms.DateField(
        widget=forms.TextInput(     
        attrs={'type': 'date'} 
    )
    )
    class Meta:
        model = LeaveManagement
        exclude = ['employee_id']