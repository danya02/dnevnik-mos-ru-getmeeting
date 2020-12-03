import requests
from database import *
import json

def cookiejar_valid(cj):
    cookies = json.loads(cj.data)
    req = requests.get('https://dnevnik.mos.ru/core/api/student_profiles/' + str(cookies['profile_id']), cookies=cookies)
    return req.status_code == 200
