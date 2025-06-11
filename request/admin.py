from django.contrib import admin
from .models import Environment, Collection, APIRequest, RequestHistory, SavedResponse


@admin.register(Environment)
class EnvironmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('name', 'user__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('name', 'description', 'user__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(APIRequest)
class APIRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'method', 'url', 'user', 'collection', 'created_at')
    list_filter = ('method', 'body_type', 'created_at', 'user', 'collection')
    search_fields = ('name', 'url', 'description', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'method', 'url', 'description', 'user', 'collection', 'environment')
        }),
        ('پارامترها و هدرها', {
            'fields': ('params', 'headers')
        }),
        ('احراز هویت', {
            'fields': ('auth_type', 'auth_data')
        }),
        ('بدنه درخواست', {
            'fields': ('body_type', 'body_raw', 'body_raw_type', 'body_form_data', 'body_urlencoded')
        }),
        ('تنظیمات', {
            'fields': ('timeout', 'follow_redirects')
        }),
        ('زمان‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(RequestHistory)
class RequestHistoryAdmin(admin.ModelAdmin):
    list_display = ('request', 'method', 'status_code', 'status', 'response_time', 'executed_at')
    list_filter = ('status', 'method', 'executed_at', 'user')
    search_fields = ('request__name', 'url', 'user__username')
    readonly_fields = ('executed_at',)
    fieldsets = (
        ('اطلاعات درخواست', {
            'fields': ('request', 'user', 'method', 'url', 'headers', 'body')
        }),
        ('اطلاعات پاسخ', {
            'fields': ('status_code', 'response_headers', 'response_body', 'response_time', 'response_size')
        }),
        ('وضعیت', {
            'fields': ('status', 'error_message')
        }),
        ('زمان', {
            'fields': ('executed_at',)
        })
    )


@admin.register(SavedResponse)
class SavedResponseAdmin(admin.ModelAdmin):
    list_display = ('name', 'history', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('name', 'notes', 'user__username')
    readonly_fields = ('created_at',)
