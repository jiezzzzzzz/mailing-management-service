import requests
import os
import django
import time
from django.core.management.base import BaseCommand
from dotenv import load_dotenv
from .models import Mailing, Client, Message, Tag


class Command(BaseCommand):

    def handle(self, *args, **options):
        load_dotenv()
        token = os.getenv("TOKEN_SENDER")

        local_time = django.utils.timezone.localtime()

        url = 'https://probe.fbrq.cloud/v1/send/0'

        current_mailings = Mailing.objects.filter(
            launched_at__lte=local_time,
            completed_at__gte=local_time,
        ).prefetch_related('clients')

        for mailing in current_mailings:
            clients = mailing.clients.all()
            for client in clients:
                url = f'https://probe.fbrq.cloud/v1/send/{mailing.id}'
                payload = {
                    "id": mailing.id,
                    "phone": int(str(client.phonenumber)[1:]),
                    "text": mailing.text,
                }
                headers = {
                    "Authorization": f"Bearer {token}",
                }
                try:
                    response = requests.post(url, headers=headers, json=payload)
                    response.raise_for_status()
                    if response.json()['message'] == 'OK':
                        message = Message.objects.create(
                            mailing=Mailing.objects.get(id=mailing.id),
                            send_status=True,
                        )
                        add_clients = Client.objects.filter(id=client.id)
                        message.clients.set(add_clients)
                    else:
                        message = Message.objects.create(
                            mailing=Mailing.objects.get(id=mailing.id),
                            send_status=False,
                        )
                        add_clients = Client.objects.filter(id=client.id)
                        message.clients.set(add_clients)
                except requests.exceptions.ConnectionError:
                    print('Произошел разрыв сетевого соединения. Ожидаем 1 минуту.')
                    time.sleep(60)
                    continue
                except requests.exceptions.HTTPError:
                    print('Что-то не так с адресом страницы')
                    continue


if __name__ == "__main__":
    Command().handle()