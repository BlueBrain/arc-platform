from django.urls import path
from arcv2_platform.resources import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('resources/category/validate/<int:pk>', views.validate_category, name="validate-category"),
    path('resources/item/validate/<int:pk>', views.validate_item, name="validate-item"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
