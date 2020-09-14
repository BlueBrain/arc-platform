from django.contrib import admin

from arcv2_platform.matchmaking.models import Request, Supply, Match


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['creation_time', 'resource', 'resourceType', 'category', 'item', 'quantity', 'priority', 'status']
    list_filter = ['resource', 'resourceType', 'status']


@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    list_display = ['creation_time', 'resource', 'resourceType', 'category', 'item', 'quantity', 'status']
    list_filter = ['resource', 'status']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['request', 'supply', 'creation_time', 'quantity', 'status']
    list_filter = ['status']
