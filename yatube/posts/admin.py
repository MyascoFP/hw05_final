from django.contrib import admin

from .models import Comment, Follow, Group, Post


@admin.register(Post)
class Post(admin.ModelAdmin):
    list_display = ('pk', 'text', 'created', 'author', 'group')
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'
    pass


@admin.register(Group)
class Group(admin.ModelAdmin):
    pass


@admin.register(Comment)
class Comment(admin.ModelAdmin):
    pass


@admin.register(Follow)
class Follow(admin.ModelAdmin):
    pass
