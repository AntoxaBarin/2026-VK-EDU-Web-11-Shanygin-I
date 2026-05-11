from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Answer, AnswerLike, Profile, Question, QuestionLike, Tag


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Профиль"


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    raw_id_fields = ("author",)
    fields = ("author", "text", "is_correct", "votes", "created_at")
    readonly_fields = ("created_at",)


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "avatar")
    search_fields = ("user__username", "user__email")
    raw_id_fields = ("user",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "votes", "created_at")
    search_fields = ("title", "text", "author__username")
    list_filter = ("created_at", "tags")
    raw_id_fields = ("author",)
    inlines = [AnswerInline]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("author")
            .prefetch_related("tags")
        )


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("__str__", "author", "votes", "is_correct", "created_at")
    search_fields = ("text", "author__username", "question__title")
    list_filter = ("is_correct", "created_at")
    raw_id_fields = ("author", "question")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("author", "question")


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ("user", "question")
    search_fields = ("user__username", "question__title")
    raw_id_fields = ("user", "question")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "question")


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ("user", "answer")
    search_fields = ("user__username",)
    raw_id_fields = ("user", "answer")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "answer")
