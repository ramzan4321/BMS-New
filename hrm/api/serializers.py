from rest_framework import serializers
from hrm.models import LeaveManagement, Employees

class LeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveManagement
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employees
        fields = '__all__'