
import socket

from smtplib import SMTP_SSL, SMTP
from urllib.parse import urlparse

import socks

from django.core.mail.backends.smtp import EmailBackend as DjangoEmailBackend

from arcv2_platform.config.config import config


def create_connection(address, timeout, source_address):
    if config.http_proxy:
        parsed_http_proxy_url = urlparse(config.http_proxy)
        return socks.create_connection(
            address,
            timeout,
            source_address,
            proxy_type=socks.HTTP,
            proxy_addr=parsed_http_proxy_url.hostname,
            proxy_port=parsed_http_proxy_url.port
        )

    return socket.create_connection(address, timeout, source_address)


class PROXIED_SMTP_SSL(SMTP_SSL):
    def _get_socket(self, host, port, timeout):
        new_socket = create_connection((host, port), timeout, self.source_address)
        new_socket = self.context.wrap_socket(new_socket, server_hostname=self._host)
        return new_socket


class PROXIED_SMTP(SMTP):
    def _get_socket(self, host, port, timeout):
        return create_connection((host, port), timeout, self.source_address)


class EmailBackend(DjangoEmailBackend):
    @property
    def connection_class(self):
        return PROXIED_SMTP_SSL if self.use_ssl else PROXIED_SMTP
