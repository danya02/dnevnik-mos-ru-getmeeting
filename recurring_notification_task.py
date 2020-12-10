import notification_method
import datetime
from database import *

def send_asap_notifications():
    meeting = Meeting.get_or_none(Meeting.notified_asap==False)
    while meeting:
        batch = meeting.batch
        notification_methods = list(meeting.group.notification_methods)
        for method in notification_methods:
            method = notification_method.get_notification_method(method)
            method.notify_asap_batch(batch)
        Meeting.update(notified_asap=True).where(Meeting.batch == batch).execute()
        meeting = Meeting.get_or_none(Meeting.notified_asap==False)

def send_starting_soon_notifications():
    now = datetime.datetime.now()
    in_future_window = now + datetime.timedelta(0, 15*60)  # 15 minutes
    meetings_to_notify = Meeting.select().where(Meeting.notified_before_lesson == False).where(Meeting.starts_at < in_future_window)
    for meeting in meetings_to_notify:
        for notif_method in meeting.group.notification_methods:
            notif_method = notification_method.get_notification_method(notif_method)
            notif_method.notify_before_start(meeting)
        meeting.notified_before_lesson = True
        meeting.save()

send_asap_notifications()
send_starting_soon_notifications()
