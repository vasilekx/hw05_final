"""The admin site configuration"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Post, Group, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'created', 'author', 'group')
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'post', 'post_pk', 'text', 'author', 'created')
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'

    def post_pk(self, obj):
        return obj.post.pk

    post_pk.admin_order_field = 'post__pk'
    post_pk.short_description = _('Ключ поста')


admin.site.register(Comment, CommentAdmin)
admin.site.register(Group)
admin.site.register(Post, PostAdmin)

