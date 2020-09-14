from django.urls import path
from arcv2_platform.matchmaking import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('requests/', views.RequestListView.as_view(), name="requests"),
    path('requests/<int:pk>', views.RequestDetailView.as_view(), name="request-detail"),
    path('requests/new', views.request_create, name="requests-create"),
    path('requests/validate/<int:pk>', views.validate_request, name='request-validate'),
    path('requests/set-priority/<int:pk>', views.set_request_priority, name='request-set-priority'),
    path('requests/set-sensitivity/<int:pk>', views.set_request_sensitivity, name='request-set-sensitivity'),
    path('requests/reject/<int:pk>', views.reject_request, name='request-reject'),
    path('requests/edit/<int:pk>', views.request_create, name="requests-edit"),
    path('requests/close/<int:pk>', views.close_request, name="request-close"),
    path('requests/archive/<int:pk>', views.archive_request, name="request-archive"),
    path('requests/resurrect/<int:pk>', views.resurrect_request, name="request-resurrect"),
    path('requests/unexpire/<int:pk>', views.unexpire_request, name="request-unexpire"),
    path('requests/reject/<int:pk>/<int:match_id>', views.reject_attribution, name="request-reject-attribution"),
    path('requests/complete/<int:pk>/<int:match_id>', views.complete_attribution, name="request-complete-attribution"),
    path('requests/attribute/<int:pk>/<int:supply_id>', views.attribute_supply, name="request-supply-attribute"),
    path('requests/hold/<int:pk>/<int:match_id>', views.hold_attribution, name="request-supply-hold"),
    path('requests/validate/<int:pk>/<int:match_id>', views.validate_attribution, name="request-validate-attribution"),
    path('supplies/', views.SupplyListView.as_view(), name="supplies"),
    path('supplies/<int:pk>', views.SupplyDetailView.as_view(), name="supplies-detail"),
    path('supplies/new', views.supply_create, name="supplies-create"),
    path('supplies/edit/<int:pk>', views.supply_create, name="supplies-edit"),
    path('supplies/close/<int:pk>', views.close_supply, name="supply-close"),
    path('supplies/archive/<int:pk>', views.archive_supply, name="supply-archive"),
    path('api/requests/', views.ListCreateRequestAPIView.as_view(), name='request-api'),
    path('api/supplies/', views.ListCreateSupplyAPIView.as_view(), name='supply-api'),

]

urlpatterns = format_suffix_patterns(urlpatterns)
