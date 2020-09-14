from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import resolve

from arcv2_platform.app.log import log
from arcv2_platform.config.config import config


class IpFilterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if config.allowed_ip_addresses is not None:
            ip_list = map(lambda x: x.strip(), config.allowed_ip_addresses.split(','))
            # This is specific to this project where we want to check the IP of the proxy.
            # It does not check the IP address of the client !
            ip = request.META.get('HTTP_X_FORWARDED_FOR').split(',')[-1].strip()

            if ip not in ip_list:
                log.warning(f'IP filtering rejected request from IP address {ip}')
                return HttpResponseForbidden()

        return self.get_response(request)


class TermsOfServiceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.has_accepted_tos:
            route_name = resolve(request.path_info).url_name
            if route_name not in ['terms-of-service', 'logout']:
                return redirect('terms-of-service')

        return self.get_response(request)
