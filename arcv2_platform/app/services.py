
from django.core.mail import get_connection, EmailMultiAlternatives, send_mail as django_send_mail
from django.template.loader import render_to_string

from arcv2_platform.config.config import config


class HtmlEmail(EmailMultiAlternatives):
    @classmethod
    def from_template(cls, subject, template, context, recipient_list, recipient_cc_list=[]):
        text = render_to_string(f'{template}.txt', context)
        html = render_to_string(f'{template}.html', context)
        return cls(subject, text, html, recipient_list, recipient_cc_list=recipient_cc_list)

    def __init__(self, subject, text_message, html_message, recipient_list, recipient_cc_list=[]):
        super().__init__(
            f'{config.email.subject_prefix} {subject}',
            text_message,
            config.email.default_from,
            recipient_list,
            cc=recipient_cc_list
        )
        self.attach_alternative(html_message, 'text/html')


# TODO: refactor scripts to use new HtmlEmail class
def send_mail(subject, message, recipient_list, html_message=None, fail_silently=False):
    return django_send_mail(
        f'{config.email.subject_prefix} {subject}',
        message,
        config.email.default_from,
        recipient_list,
        html_message=html_message,
        fail_silently=fail_silently
    )


def send_mass_html_mail(emails, fail_silently=False, connection=None):
    connection = connection or get_connection(fail_silently=fail_silently)
    connection.open()
    connection.send_messages(emails)
    connection.close()
