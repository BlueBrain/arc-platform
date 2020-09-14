from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from arcv2_platform.app.decorators import role_required
from arcv2_platform.app.models import Role
from arcv2_platform.resources.models import Category, CategoryItem


@login_required
@role_required(roles=[Role.moderator, Role.validator])
def validate_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)

    category.is_validated = True
    category.save()

    return _redirect_to_model_detail(request)


@login_required
@role_required(roles=[Role.moderator, Role.validator])
def validate_item(request, pk=None):
    item = get_object_or_404(CategoryItem, pk=pk)

    item.is_validated = True
    item.category.is_validated = True
    item.save()
    item.category.save()

    return _redirect_to_model_detail(request)


def _redirect_to_model_detail(request):
    supply_id = request.GET.get('supply_id', False)
    request_id = request.GET.get('request_id', False)

    if supply_id:
        return redirect('supplies-detail', pk=supply_id)
    elif request_id:
        return redirect('request-detail', pk=request_id)
    else:
        return redirect('dashboard')
