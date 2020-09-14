from rest_framework.authtoken.models import Token
from django.urls import reverse

from arcv2_platform.config.config import config
from arcv2_platform.app.services import HtmlEmail
from arcv2_platform.matchmaking.models import Supply
from arcv2_platform.users.models import User


def run():
    print('Notifying suppliers to archive unavailable supply...')

    send_archive_supplies_reminder()

    print('Done')


def send_archive_supplies_reminder():
    supplies_queryset = Supply.objects.filter(
        status__in=[Supply.Status.ATTRIBUTED, Supply.Status.AVAILABLE],
    )

    supplier_ids = supplies_queryset.order_by('creator').values_list('creator', flat=True).distinct('creator')

    for supplier_id in supplier_ids:
        supplier = User.objects.get(id=supplier_id)

        if not supplier.notification_enabled:
            continue

        supplies = supplies_queryset.filter(creator=supplier_id)

        subject = 'Archive supplies reminder'
        template = 'email/supplies_to_archive_reminder__supplier_email'
        unsubscribe_url = reverse('unsubscribe', kwargs={'user_token': Token.objects.get(user=supplier)})
        context = {
            'supplies': supplies,
            'deployment_base_url': config.deployment.base_url,
            'unsubscribe_url': f'{config.deployment.base_url}{unsubscribe_url}'
        }
        recipient = supplier.email

        email = HtmlEmail.from_template(subject, template, context, [recipient])

        sent_num = email.send()
        status = 'OK' if sent_num == 1 else 'FAIL'
        print(f'{recipient:.<40} Supplies: {len(supplies):<4} Email send: {status}')
