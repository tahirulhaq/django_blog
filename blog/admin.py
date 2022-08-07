from django.contrib import admin
from .models import Post, Comment, Reply
from django.contrib.sessions.models import Session

# Register your models here.

# customize how the data is shown in admin panel


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'status', 'created_on')
    list_filter = ("status",)
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
admin.site.register(Reply)
admin.site.register(Session)
