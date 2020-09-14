from django.contrib import admin

from arcv2_platform.users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['firstname', 'lastname', 'username', 'email', 'phone', 'is_active', 'is_super_admin',
                    'is_moderator', 'is_validator']
    list_filter = ['is_active', 'is_super_admin', 'is_moderator', 'is_validator', 'is_requester']
    search_fields = ['firstname', 'lastname', 'email', 'phone']
