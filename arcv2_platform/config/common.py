"""
Configuration for all environments. Value can be overridden in per-env config files
Or using the corresponding environment variable at runtime.
"""
common = {
    'APP_DJANGO_SECRET': 'default',
    'APP_DEBUG': 'True',

    'APP_LOGLEVELS_DJANGO': 'INFO',
    'APP_LOGLEVELS_APP': 'DEBUG',

    'APP_DB_NAME': 'arcv2_platform',
    'APP_DB_USER': 'postgres',
    'APP_DB_PASSWORD': 'postgres',
    'APP_DB_HOST': 'db',
    'APP_DB_PORT': '5432',

    'APP_ALLOW_PASSWORD_LOGIN': True,

    'APP_EMAIL_DEFAULT_SUBJECT_PREFIX': '[ARC test]',

    'APP_DEPLOYMENT_BASE_URL': 'http://localhost:8000',

    'APP_REQUEST_EXPIRATION_DAYS': 14,
    'APP_REQUEST_EXPIRATION_HOLD_DAYS': 3,

    'EMAIL_BACKEND': 'arcv2_platform.core.mail.backends.smtp.EmailBackend',
}
