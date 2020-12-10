from peewee import *
import datetime
import uuid
import json
import logging
import requests
import dateutil.parser

db = MySQLDatabase('dnevnik', user='dnevnik', password='dnevnik')

class MyModel(Model):
    class Meta:
        database = db

def create_table(cls):
    db.create_tables([cls])
    return cls

@create_table
class Group(MyModel):
    name = CharField(unique=True)

@create_table
class Probe(MyModel):
    name = CharField()
    secret_key = CharField(unique=True, default=lambda: str(uuid.uuid4()))
    group = ForeignKeyField(Group)


@create_table
class CookieJar(MyModel):
    submitter = ForeignKeyField(Probe)
    data = TextField()
    submitted_at = DateTimeField(default=datetime.datetime.now)
    is_valid = BooleanField(default=True)


@create_table
class MeetingBatch(MyModel):
    fetched_at = DateTimeField(default=datetime.datetime.now)

def parse_date(date):
    return dateutil.parser.isoparse(date)

@create_table
class Meeting(MyModel):
    group = ForeignKeyField(Group)
    meeting_id = IntegerField(unique=True)
    fetched_at = DateTimeField(default=datetime.datetime.now)
    batch = ForeignKeyField(MeetingBatch, backref='meetings', null=True)

    meeting_link = TextField()
    data = TextField()
    lesson_name = CharField()
    starts_at = DateTimeField()
    created_at = DateTimeField()
    notified_asap = BooleanField(default=False)
    notified_before_lesson = BooleanField(default=False)
    
    @staticmethod
    def create_from_meeting_id(id, fetched_using_cj, batch=None):
        logging.info('Creating meeting by ID %d', id)
        req = requests.get('https://dnevnik.mos.ru/vcs/links?scheduled_lesson_id='+str(id))
        if req.status_code == 204:
            logging.warn('Meeting by ID %d does not exist??!', id)
            return None
        elif req.status_code == 200:
            data = req.json()
            return Meeting.create(meeting_id=id, data=json.dumps(data), lesson_name=data['_embedded']['link_views'][0]['link_name'], 
                    starts_at=parse_date(data['_embedded']['link_views'][0]['start_date_time']),
                    created_at=parse_date(data['_embedded']['link_views'][0]['sent_date_time']),
                    meeting_link=data['_embedded']['link_views'][0]['link_url'],
                    group=fetched_using_cj.submitter.group, batch=batch)
        else:
            logging.error('Unexpected status code: %d %s %s', requests.status_code,'\n', req.text)
            return None


@create_table
class NotificationMethod(MyModel):
    group = ForeignKeyField(Group, backref='notification_methods')
    method_name = CharField()
    props = TextField()
