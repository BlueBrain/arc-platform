import environ
import os
import importlib

from arcv2_platform.config.common import common


env = os.getenv('SERVER_ENV', 'local')


@environ.config()
class AppConfig:
    name = 'arcv2_platform'
    env = env
    django_secret = environ.var()
    debug = environ.bool_var()
    allowed_ip_addresses = environ.var(default=None)
    allow_password_login = environ.bool_var(default=False)
    http_proxy = environ.var(name='HTTP_PROXY', default=None)
    https_proxy = environ.var(name='HTTPS_PROXY', default=None)
    sentry_dsn = environ.var(default=None)

    @environ.config
    class LoggerConfig:
        django = environ.var()
        app = environ.var()
    loglevels = environ.group(LoggerConfig)

    @environ.config
    class DBConfig:
        name = environ.var()
        user = environ.var()
        password = environ.var()
        host = environ.var()
        port = environ.var(converter=int)
    db = environ.group(DBConfig)

    @environ.config
    class EmailConfig:
        backend = environ.var(name='EMAIL_BACKEND', default=None)
        host = environ.var(name='EMAIL_HOST', default=None)
        port = environ.var(name='EMAIL_PORT', default=465, converter=int)
        host_user = environ.var(name='EMAIL_HOST_USER', default=None)
        host_password = environ.var(name='EMAIL_HOST_PASSWORD', default=None)
        use_tls = environ.bool_var(name='EMAIL_USE_TLS', default=False)
        use_ssl = environ.bool_var(name='EMAIL_USE_SSL', default=True)
        default_from = environ.var(name='DEFAULT_FROM_EMAIL', default='noreply@arc.dev')
        subject_prefix = environ.var(name='APP_EMAIL_DEFAULT_SUBJECT_PREFIX')
    email = environ.group(EmailConfig)

    @environ.config
    class Deployment:
        base_url = environ.var(name='APP_DEPLOYMENT_BASE_URL')
    deployment = environ.group(Deployment)

    @environ.config
    class Request:
        expiration_days = environ.var(name='APP_REQUEST_EXPIRATION_DAYS', converter=int)
        expiration_hold_days = environ.var(name='APP_REQUEST_EXPIRATION_HOLD_DAYS', converter=int)
    request = environ.group(Request)


print('===========================================================')
print(f'Welcome to {AppConfig.name}. Using configuration SERVER_ENV={env}')
override = importlib.import_module('arcv2_platform.config.%s' % env)

config = environ.to_config(
    AppConfig,
    environ={**common, **override.config, **os.environ}
)

print('App configuration loaded:')
print(config)
print('===========================================================')
