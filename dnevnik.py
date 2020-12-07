import requests
from database import *
import json
import logging
import itertools

def get_with_cookiejar(url, cj, **kwargs):
    cookies = json.loads(cj.data)
    req = requests.get(url, cookies=cookies, headers={'Accept': 'application/json'}, **kwargs)
    return req

def cookiejar_valid(cj):
    logging.debug('Checking if cookie jar', cj, 'is valid')
    cookies = json.loads(cj.data)
    req = get_with_cookiejar('https://dnevnik.mos.ru/core/api/student_profiles/' + str(cookies['profile_id']), cj)
    if req.status_code == 200:
        logging.info('Cookie jar', cj, 'is valid')
        return True
    logging.warn('Cookie jar', cj, 'is not valid')
    return False


def get_user_group_list(cj):
    logging.debug('Getting group list for cookie jar', cj)
    cookies = json.loads(cj.data)
    req = get_with_cookiejar('https://dnevnik.mos.ru/core/api/student_profiles/' + str(cookies['profile_id']), cj).json()
    grp = req['groups']
    logging.debug('User has', len(grp), 'groups')
    return grp


def get_scheduled_lesson_ids(cj, for_date):
    logging.debug("Getting scheduled lessons using cookie jar", cj, "and date", for_date.isoformat())
    groups = get_user_group_list(cj)
    groups_commasep = ','.join(map(lambda x: str(x['id']), groups))
    cookies = json.loads(cj.data)
    url = 'https://dnevnik.mos.ru/jersey/api/schedule_items'
    date = for_date.isoformat()
    params = {'generate_eom_links':'true', 'from': date, 'to': date, 'group_id': groups_commasep, 'student_profile_id': cookies['profile_id']}
    req = get_with_cookiejar(url, cj, params=params)
    ids = []
    for i in req.json():
        logging.debug("Got scheduled lesson", i)
        ids.append(i['id'])
    return ids

def create_db_lessons(cj, for_date):
    logging.debug("Creating meetings for cookie jar", cj, "and date", for_date.isoformat())
    meetings = []
    for id in get_scheduled_lesson_ids(cj, for_date):
        try:
            meetings.append(Meeting.create_from_meeting_id(id, cj))
        except IntegrityError:
            logging.debug("Lesson by id", id, "already in database, ignoring")
    return meetings
