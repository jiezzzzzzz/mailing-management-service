from datetime import datetime
from django.db import models


class Mailing(models.Model):
    mailing_id = models.CharField(max_length=30, unique=True)
    started_at = models.DateTimeField()
    message_text = models.TextField()
    mailing_filter = models.CharField(max_length=30)
    ended_at = models.DateTimeField()

    def get_unsent_messages(self):
        return self.messages.filter(sent=False)

    def on_time(self):
        started_at = self.started_at
        ended_at = self.ended_at
        if started_at.timestamp() < datetime.now().timestamp() < ended_at.timestamp():
            return True


class Client(models.Model):
    client_id = models.CharField(max_length=30, unique=True)
    phone = models.CharField(max_length=11, unique=True)
    mobile_operator_code = models.CharField(max_length=3)
    tag = models.CharField(max_length=30)
    time_zone = models.CharField(max_length=30)


class Message(models.Model):
    message_id = models.CharField(max_length=30, unique=True)
    sent_at = models.DateTimeField(null=True)
    sent = models.BooleanField(default=False)
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name="messages")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="messages")

    def is_sent(self):
        self.sent = True
        self.save()

    def set_sent_at_now(self):
        self.sent_at = datetime.now()
        self.save()


class Tag(models.Model):
    title = models.CharField('Тег', max_length=20, unique=True)

    def __str__(self):
        return self.title