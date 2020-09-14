
from arcv2_platform.app.services import send_mass_html_mail, HtmlEmail
from arcv2_platform.users.models import User
from arcv2_platform.config.config import config


def notify_validators_w_new_match(request):
    subject = 'A new match created'
    template = 'email/match_created__validators_email'
    context = {'request': request, 'deployment_base_url': config.deployment.base_url}
    recipients = [validator.email for validator in User.validators()]

    emails = [
        HtmlEmail.from_template(subject, template, context, [recipient])
        for recipient
        in recipients
    ]

    send_mass_html_mail(emails)


def notify_moderators_w_open_request(request):
    subject = 'A new request opened'
    template = 'email/request_opened__moderators_email'
    context = {'request': request, 'deployment_base_url': config.deployment.base_url}
    recipients = [moderator.email for moderator in User.moderators()]

    emails = [
        HtmlEmail.from_template(subject, template, context, [recipient])
        for recipient
        in recipients
    ]

    send_mass_html_mail(emails)


def notify_validators_w_submitted_request(request):
    subject = 'A new request submitted'
    template = 'email/request_submitted__validators_email'
    context = {'request': request, 'deployment_base_url': config.deployment.base_url}
    recipients = [validator.email for validator in User.validators()]

    emails = [
        HtmlEmail.from_template(subject, template, context, [recipient])
        for recipient
        in recipients
    ]

    send_mass_html_mail(emails)


def notify_requester_w_validated_request(request):
    subject = 'A request validated'
    template = 'email/request_validated__requester_email'
    context = {'request': request, 'deployment_base_url': config.deployment.base_url}
    recipient = request.creator.email

    email = HtmlEmail.from_template(subject, template, context, [recipient])
    email.send()


def notify_requester_w_rejected_request(request):
    subject = 'A request rejected'
    template = 'email/request_rejected__requester_email'
    context = {'request': request, 'deployment_base_url': config.deployment.base_url}
    recipient = request.creator.email

    email = HtmlEmail.from_template(subject, template, context, [recipient])
    email.send()


def notify_supplier_w_completed_match(match):
    subject = 'A match validated'
    template = 'email/match_completed__supplier_email'
    context = {'match': match, 'deployment_base_url': config.deployment.base_url}
    recipient = match.supply.creator.email

    email = HtmlEmail.from_template(subject, template, context, [recipient])
    email.send()


def notify_all_w_validated_match(match):
    subject = 'A match validated'
    template = 'email/match_validated__all_email'
    context = {'match': match, 'deployment_base_url': config.deployment.base_url}

    requester = match.request.creator.email
    supplier = match.supply.creator.email
    email_to = list(set([requester, supplier]))

    email_cc = [
        validator.email
        for validator
        in User.validators()
        if validator.email not in email_to
    ]

    email = HtmlEmail.from_template(subject, template, context, email_to, email_cc)
    email.send()
