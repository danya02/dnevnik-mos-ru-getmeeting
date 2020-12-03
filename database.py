from peewee import *
import datetime
import uuid
import json

db = MySQLDatabase('dnevnik', user='dnevnik', password='dnevnik')

class MyModel(Model):
    class Meta:
        database = db

def create_table(cls):
    db.create_tables([cls])
    return cls

@create_table(MyModel)
class Group(MyModel):
    name = CharField(unique=True)

@create_table(MyModel)
class Probe(MyModel):
    name = CharField()
    secret_key = UUIDField(unique=True, default=uuid.uuid4)
    group = ForeignKeyField(Group)


@create_table
class CookieJar(MyModel):
    submitter = ForeignKeyField(Probe)
    data = TextField()
    submitted_at = DateTimeField(default=datetime.datetime.now)
    is_valid = BooleanField(default=True)


@create_table
class Meeting(MyModel):
    group = ForeignKeyField(Group)
    meeting_id = IntegerField(unique=True)
    fetched_at = DateTimeField(default=datetime.datetime.now)
    data = TextField()
    lesson_name = CharField()
    starts_at = DateTimeField()
    created_at = DateTimeField()
    notified_asap = BooleanField(default=False)
    notified_before_lesson = BooleanField(default=False)
    
    @staticmethod
    def create_from_meeting_id(id):
        data = requests.get('https://dnevnik.mos.ru/vcs/links?scheduled_lesson_id='+str(id)).json()
        return Meeting.create(meeting_id=id, data=json.dumps(data), lesson_name=data['_embedded']['link_views'][0]['link_name'], 
                starts_at=datetime.datetime.fromisoformat(data['_embedded']['link_views'][0]['start_date_time']),
                created_at=datetime.datetime.fromisoformat(data['_embedded']['link_views'][0]['sent_date_time']))


@create_table
class NotificationMethod(MyModel):
    group = ForeignKeyField(Group)
    method_name = CharField()
    props = TextField()
