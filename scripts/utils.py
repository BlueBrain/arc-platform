from django.core.exceptions import ImproperlyConfigured

from arcv2_platform.config import config


def check_for_prod():
    if config.env.lower() == 'prd':
        raise ImproperlyConfigured('Trying to run seeding script with config.env = prd. I won\'t do that.')
