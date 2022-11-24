from django.http import HttpResponse
from .serializers import LeaveSerializer, EmployeeSerializer
from rest_framework.views import View
import json , io
from datetime import date, datetime
import dateutil.parser
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from hrm.models import Employees, LeaveManagement
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

class EmployeeAPI(View):
    def get(self, request, *args, **kwargs):
        json_data = request.body
        stream = io.BytesIO(json_data)
        python_data = JSONParser().parse(stream)
        id = python_data.get('id')
        if id is not None:
            emp = Employees.objects.get(id=id)
            serializer = EmployeeSerializer(emp)
            res = JSONRenderer().render(serializer.data)
            return HttpResponse(res , content_type='application/json')

        emp = Employees.objects.all()
        serializer = EmployeeSerializer(emp, many=True)
        res = JSONRenderer().render(serializer.data)
        return HttpResponse(res , content_type='application/json')

@method_decorator(csrf_exempt, name="dispatch")
class LeaveAPI(View):
    def post(self, request, *args, **kwargs):
        json_data = request.body
        stream = io.BytesIO(json_data)
        python_data = JSONParser().parse(stream)
        employee_id = python_data.get('employee_id')
        leave_type = python_data.get('leave_type')
        leave_days = python_data.get('leave_days')
        date1 = (dateutil.parser.parse(leave_days)).date() # Converting string date format into python date object

        python_data['leave_days'] = date1 # Updating string date to python date object

        week_day = date1.strftime("%A") # Getting Week name from date.

        if employee_id is not None and leave_type is not None and leave_days is not None:
            
            if week_day == 'Sunday' or week_day == 'Saturday' or date.today() > date1:
                msg = {'error':'Sorry! No need for leaves on weekend or past dates.'}
                res = json.dumps(msg)
                return HttpResponse(res , content_type='application/json')

            if LeaveManagement.objects.filter(employee_id = employee_id, leave_days = date1).exists():
                msg = {'error':'Sorry! You have taken leave already.'}
                res = json.dumps(msg)
                return HttpResponse(res , content_type='application/json')

            if leave_type == 'P':
                year = datetime.now().year
                chk = LeaveManagement.objects.filter(employee_id=employee_id,leave_type='P',leave_days__year=year).count()
                usr = User.objects.get(id=employee_id)
                date_joined = usr.date_joined
                xy = date_joined.date().year
                if xy < year:
                    y_diff = year - xy
                    if y_diff >= 2:
                        chk_last_year = LeaveManagement.objects.filter(employee_id=employee_id,leave_type='P',leave_days__year=(year-1)).count()
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
                    serializer = LeaveSerializer(data = python_data)
                    if serializer.is_valid():
                        serializer.save()
                        st = f'Your Leave Application has been submitted. You have {(leave_limit-(chk+1))} Paid leave balanced...'
                        msg = {'status': st}
                        res = json.dumps(msg)
                        return HttpResponse(res , content_type='application/json')
                    msg = {'status': serializer.errors}
                    res = JSONRenderer().render(serializer.errors)
                    return HttpResponse(res , content_type='application/json')

                else:
                    msg = {'status':'Sorry! Your can not take more paid leaves...'}
                    res = json.dumps(msg)
                    return HttpResponse(res , content_type='application/json')
            else:
                serializer = LeaveSerializer(data = python_data)
                if serializer.is_valid():
                    serializer.save()
                    msg = {'status':'Your Leave Application has been submitted...'}
                    res = json.dumps(msg)
                    return HttpResponse(res , content_type='application/json')
                msg = {'status': serializer.errors}
                res = JSONRenderer().render(serializer.errors)
                return HttpResponse(res , content_type='application/json')
        else:
            msg = {'error':'Please Provide all information...'}
            res = json.dumps(msg)
            return HttpResponse(res , content_type='application/json')

