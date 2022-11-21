import requests
import json

URL = "http://127.0.0.1:8000/api/leave/"

def get_emp(id=None):
    data = {}
    if id is not None:
        data = {'id':id}
    json_data = json.dumps(data)
    r = requests.get(url=URL, data = json_data)
    data = r.json()
    print(data)

#get_emp(7)

def post_leave():
    data = {
        'employee_id':2,
        'leave_days':'2022-11-18',
        'leave_type':'U',
        'leave_reason':'Any'
    }
    json_data = json.dumps(data)
    r = requests.post(url=URL, data = json_data)
    data = r.json()
    print(data)

post_leave()