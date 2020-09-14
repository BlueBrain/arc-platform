from arcv2_platform.config.config import config


def inject_config(request):
    return {
        'config': config,
        'request_full_path': request.get_full_path(),
    }
