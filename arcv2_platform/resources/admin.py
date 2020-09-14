from django.contrib import admin

from arcv2_platform.resources.models import Resource, Category, CategoryItem, ResourceType


class ResourceInline(admin.TabularInline):
    model = Resource


class ResourceTypeInline(admin.TabularInline):
    model = ResourceType


class ItemInline(admin.TabularInline):
    model = CategoryItem


class CategoryInline(admin.TabularInline):
    model = Category


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    search_fields = ['name']
    inlines = [ResourceTypeInline]


@admin.register(ResourceType)
class ResourceTypeAdmin(admin.ModelAdmin):
    search_fields = ['name']
    inlines = [CategoryInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_filter = ['resourceType']
    inlines = [ItemInline]


@admin.register(CategoryItem)
class CategoryItemAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_filter = ['category']
