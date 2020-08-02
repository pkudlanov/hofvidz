from django.contrib import admin
from . import models


class VideoAdmin(admin.ModelAdmin):
    readonly_fields = ('id', )
    list_display = ['title', 'hall']
    list_filter = ['hall']


class HallAdmin(admin.ModelAdmin):
    list_display = ['title', 'user']
    list_filter = ['user']


admin.site.register(models.Hall, HallAdmin)
admin.site.register(models.Video, VideoAdmin)
