from datetime import datetime

import pkg_resources
from rest_framework.permissions import AllowAny

from arcv2_platform.config.config import config
from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.views import APIView

from arcv2_platform.matchmaking.models import Request, Supply, Match
from arcv2_platform.matchmaking.views import _all_resources


class InfoVersionView(APIView):
    """
    Healthcheck: Displays current project version.
    """

    permission_classes = [AllowAny]

    def get(self, request, format=None):
        # TODO : Find a better way to get the version. It seems wrong in dev...
        distrib = pkg_resources.get_distribution("arcv2_platform")

        response = {
            "name": config.name,
            "version": distrib.version,
            "env": config.env,
        }
        return Response(response)


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('start')

    resources = _all_resources()
    requests_created_today = Request.objects.filter(creation_time__date=datetime.today()).count()
    supplies_created_today = Supply.objects.filter(creation_time__date=datetime.today()).count()
    requests_validated_today = Match.objects.filter(status=Match.Status.ATTRIBUTED,
                                                    creation_time__date=datetime.today()).count()
    supplies_available = Supply.objects.filter(status=Supply.Status.AVAILABLE).count()
    requests_open = Request.objects.filter(status=Request.Status.OPEN).count()
    requests_to_be_validated = Match.objects.filter(status=Match.Status.ATTRIBUTED).count()

    return render(request, 'app/dashboard.html', {
        "resources": resources,
        "request_created_today": requests_created_today,
        "supplies_created_today": supplies_created_today,
        "request_validated_today": requests_validated_today,
        "supplies_available": supplies_available,
        "request_open": requests_open,
        "request_to_be_validated": requests_to_be_validated
    })


def start(request):
    return render(request, 'app/start.html')


def impressum(request):
    return render(request, 'app/impressum.html')
