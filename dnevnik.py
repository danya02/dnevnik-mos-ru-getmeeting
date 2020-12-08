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
    logging.debug('Checking if cookie jar %s is valid', repr(cj))
    cookies = json.loads(cj.data)
    req = get_with_cookiejar('https://dnevnik.mos.ru/core/api/student_profiles/' + str(cookies['profile_id']), cj)
    if req.status_code == 200:
        logging.info('Cookie jar %s is valid', repr(cj))
        return True
    logging.warn('Cookie jar %s is not valid', repr(cj))
    return False


def get_user_group_list(cj):
    logging.debug('Getting group list for cookie jar %s', repr(cj))
    cookies = json.loads(cj.data)
    req = get_with_cookiejar('https://dnevnik.mos.ru/core/api/student_profiles/' + str(cookies['profile_id']), cj).json()
    grp = req['groups']
    logging.info('User has %d groups', len(grp))
    return grp


def get_scheduled_lesson_ids(cj, for_date):
    logging.info("Getting scheduled lessons using cookie jar %s and date %s", repr(cj), for_date.isoformat())
    groups = get_user_group_list(cj)
    groups_commasep = ','.join(map(lambda x: str(x['id']), groups))
    cookies = json.loads(cj.data)
    url = 'https://dnevnik.mos.ru/jersey/api/schedule_items'
    date = for_date.isoformat()
    params = {'generate_eom_links':'true', 'from': date, 'to': date, 'group_id': groups_commasep, 'student_profile_id': cookies['profile_id']}
    req = get_with_cookiejar(url, cj, params=params)
    ids = []
    for i in req.json():
        logging.info("Got scheduled lesson %d", i['id'])
        ids.append(i['id'])
    return ids

def create_db_lessons(cj, for_date, batch=None):
    logging.info("Creating meetings for cookie jar %s and date %s", repr(cj), for_date.isoformat())
    with db.atomic():
        if batch is None:
            batch = MeetingBatch.create()
        meetings = []
        for id in get_scheduled_lesson_ids(cj, for_date):
            try:
                meetings.append(Meeting.create_from_meeting_id(id, cj, batch))
            except IntegrityError:
                logging.debug("Lesson by id %d already in database, ignoring", id)
        return meetings
