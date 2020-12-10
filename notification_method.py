import logging
logging.getLogger().setLevel(logging.DEBUG)
import requests
from database import *
import datetime

NOTIFICATION_METHODS = dict()

def notify_method(name):
    def class_decor(cls):
        NOTIFICATION_METHODS.update( {name: cls} )
        return cls
    return class_decor


@notify_method('discord-webhook')
class DiscordWebhook:
    CONTRIBUTED_THANKS = 'The following meetings have been contributed.'
    CONTRIBUTED_SHOW_ONLY_TEN = 'Showing only 10 meetings out of the {count} received.'
    STARTS_SOON = 'This meeting will start in just {minutes_remaining} minutes. Join now!'


    def __init__(self, props):
        self.url = props

    def send(self, text, embeds=None):
        req = requests.post(self.url, json={
            'content': text, 'embeds': embeds})
        try:
            req.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(req.text)
            raise e

    @classmethod
    def meeting_embed(cls, meeting):
        emb = {}
        emb['title'] = meeting.lesson_name
        emb['url'] = meeting.meeting_link
        emb['timestamp'] = meeting.starts_at.isoformat()

        return emb

    def notify_asap_batch(self, batch):
        meetings = Meeting.select().where(Meeting.batch == batch)
        message = self.CONTRIBUTED_THANKS
        embeds = []
        for m in meetings:
            if len(embeds) >= 10:
                message += '\n' + self.CONTRIBUTED_SHOW_ONLY_TEN.format(count=len(meetings))
                break
            embeds.append(self.meeting_embed(m))
        self.send(message, embeds)

    def notify_before_start(self, meeting):
        now = datetime.datetime.now()
        time_until_lesson = meeting.starts_at - now
        message = self.STARTS_SOON.format(minutes_remaining=int(time_until_lesson.total_seconds() // 60))
        embed = self.meeting_embed(meeting)
        self.send(message, [embed])

def get_notification_method(method):
    return NOTIFICATION_METHODS[method.method_name](method.props)
