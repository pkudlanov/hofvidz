from django.contrib import admin
from . import models


class VideoAdmin(admin.ModelAdmin):
    readonly_fields = ('id', )


admin.site.register(models.Hall)
admin.site.register(models.Video, VideoAdmin)
