from django.contrib import admin
from kagiso_auth.models import KagisoUser

from reddit.models import (
    Comment,
    CustomUser,
    ReportSubmission,
    Submission,
    Vote
)


# Register your models here.
class SubmissionInline(admin.TabularInline):
    model = Submission
    max_num = 10


class CommentsInline(admin.StackedInline):
    model = Comment
    max_num = 10


class SubmissionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'url',
        'author',
        'image',
        'image_url',
        'image_compress_url'
    )
    inlines = [CommentsInline]


class KagisoUserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'first_name',
        'last_name',
        'email',
        'is_active',
        'is_staff',
        'is_superuser',
        'last_sign_in_via',
        'created'
    )

    readonly_fields = (
        'id',
        'first_name',
        'last_name',
        'email',
        'email_confirmed',
        'is_active',
        'is_staff',
        'is_superuser',
        'last_sign_in_via',
        'created',
        'created_via',
        'profile',
        'password',
        'last_login',
        'modified',
        'user_permissions'
    )

    def has_add_permission(self, request, obj=None):
        return False


class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        '_user',
        'moderator',
        'admin',
        'created_at'
    )

    def _user(self, obj):
        return obj.user.id


class ReportSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'reported_by',
        'submission',
        'created_at'
    )


admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Comment)
admin.site.register(ReportSubmission)
admin.site.register(Vote)
admin.site.register(KagisoUser, KagisoUserAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
