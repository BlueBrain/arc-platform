
from django.utils import timezone
from django.db.models import F, Q, Count

from arcv2_platform.config.config import config
from arcv2_platform.app.services import HtmlEmail
from arcv2_platform.matchmaking.models import Request
from arcv2_platform.users.models import User


def run():
    print('Flagging expiring requests and notifying validators...')
    process_expiring_requests()

    print('Archiving expired requests...')
    archive_expired_requests()

    print('Done')


def archive_expired_requests():
    archiving_time = timezone.now() - timezone.timedelta(days=config.request.expiration_hold_days)
    queryset = Request.objects.filter(
        status=Request.Status.OPEN,
        expiry_notification_time__isnull=False,
        expiry_notification_time__lt=archiving_time,
    )

    request_ids_to_archive = [
        request.id
        for request
        in queryset
        if not request.has_attributed_supplies
    ]

    queryset_to_archive = Request.objects.filter(id__in=request_ids_to_archive)
    total_archived = queryset_to_archive.update(status=Request.Status.ARCHIVED)

    for request in queryset_to_archive:
        print(f'id: {request.id} update_time: {request.update_time} {request}')

    print(f'Total {total_archived} request(s) archived')


def process_expiring_requests():
    now = timezone.now()
    expiration_time = now - timezone.timedelta(days=config.request.expiration_days)

    # Reset expiry_notification_time for requests edited after the time
    # when expiry notification has been sent (in last REQUEST_EXPIRATION_DAYS)
    to_reset = Request.objects.filter(
        status=Request.Status.OPEN,
        expiry_notification_time__isnull=False,
    ).annotate(
        matches_count=Count('matches')
    ).filter(
        Q(
            update_time__gt=F('expiry_notification_time'),
        ) | Q(
            matches_count__gt=0
        ),
    )
    print(f'Resetting expiry notification time for requests lately modified or containing matches')
    for request in to_reset:
        print(request)

    total_reset = to_reset.update(
        expiry_notification_time=None
    )
    print(f'Total {total_reset} reset')

    # Flag expiring requests and send a notification to validators
    expiring_requests = Request.objects.filter(
        status=Request.Status.OPEN,
        expiry_notification_time__isnull=True,
    ).annotate(
        matches_count=Count('matches')
    ).filter(
        update_time__lt=expiration_time,
        matches_count=0
    )

    if len(expiring_requests) == 0:
        print('No expiring requests found')
        return

    print('Notifying validators via email')
    notify_validators(expiring_requests)

    total_expiring = len(expiring_requests)
    print('Flagging requests as expiring')
    for request in expiring_requests:
        print(request)
    expiring_requests.update(expiry_notification_time=now)
    print(f'Total {total_expiring} flagged as expiring')


def notify_validators(requests):
    subject = 'Expiring requests'
    recipients = [validator.email for validator in User.validators()]
    template = 'email/request_expiring__validator_email'
    context = {'requests': requests, 'deployment_base_url': config.deployment.base_url}

    for recipient in recipients:
        email = HtmlEmail.from_template(subject, template, context, [recipient])
        sent_num = email.send()
        status = 'OK' if sent_num == 1 else 'FAIL'
        print(f'{recipient:.<40} {status}')
