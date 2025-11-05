from django.contrib import admin
from .models import AccessCode, Announcement, Vistor


class VistorAdmin(admin.ModelAdmin):
    list_display = ('id', 'fullname', 'phone_number', 'description', 'created_at', 'signed_in', 'signed_out', )
    search_fields = ('fullname', 'phone_number', 'description', )
    list_filter = ('created_at', 'signed_in', 'signed_out', )
    ordering = ('-created_at', 'signed_in', 'signed_out',)


class AccessCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'code_type', 'start_time', 'end_time', 'status', 'created_at', 'updated_at',)
    search_fields = ('code', 'code_type', 'status', )
    list_filter = ('code_type', 'status', 'created_at', 'updated_at',)
    ordering = ('-created_at', 'status','updated_at', )


class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'signed_by', 'created_at', 'updated_at',)
    search_fields = ('title', 'signed_by', )
    list_filter = ('created_at', 'updated_at',)
    ordering = ('-created_at', 'updated_at',)

admin.site.register(Vistor, VistorAdmin)
admin.site.register(AccessCode, AccessCodeAdmin)
admin.site.register(Announcement, AnnouncementAdmin)