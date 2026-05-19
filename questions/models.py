from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count
from django.urls import reverse


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Пользователь",
    )
    avatar = models.ImageField(
        upload_to="avatars/", null=True, blank=True, verbose_name="Аватар"
    )

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return f"Профиль {self.user.username}"


class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True, verbose_name="Название")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class QuestionManager(models.Manager):
    def _base_qs(self):
        return (
            self.select_related("author", "author__profile")
            .prefetch_related("tags")
            .annotate(answers_count=Count("answers", distinct=True))
        )

    def new(self):
        return self._base_qs().order_by("-created_at")

    def hot(self):
        return self._base_qs().order_by("-votes")

    def by_tag(self, tag_name):
        return self._base_qs().filter(tags__name=tag_name).order_by("-created_at")


class Question(models.Model):
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="questions", verbose_name="Автор"
    )
    tags = models.ManyToManyField(
        Tag, blank=True, related_name="questions", verbose_name="Теги"
    )
    votes = models.IntegerField(default=0, verbose_name="Голоса")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    objects = QuestionManager()

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("question", kwargs={"question_id": self.pk})


class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Вопрос",
    )
    text = models.TextField(verbose_name="Текст")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="answers", verbose_name="Автор"
    )
    is_correct = models.BooleanField(default=False, verbose_name="Правильный")
    votes = models.IntegerField(default=0, verbose_name="Голоса")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"

    def __str__(self):
        return f'Ответ #{self.pk} на "{self.question.title}"'


class QuestionLike(models.Model):
    LIKE = 1
    DISLIKE = -1
    VALUE_CHOICES = [(LIKE, "Like"), (DISLIKE, "Dislike")]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="question_likes",
        verbose_name="Пользователь",
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="likes", verbose_name="Вопрос"
    )
    value = models.SmallIntegerField(
        choices=VALUE_CHOICES, default=LIKE, verbose_name="Значение"
    )

    class Meta:
        unique_together = ("user", "question")
        verbose_name = "Лайк вопроса"
        verbose_name_plural = "Лайки вопросов"

    def __str__(self):
        return f"{self.user.username} → {self.question.title}"


class AnswerLike(models.Model):
    LIKE = 1
    DISLIKE = -1
    VALUE_CHOICES = [(LIKE, "Like"), (DISLIKE, "Dislike")]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="answer_likes",
        verbose_name="Пользователь",
    )
    answer = models.ForeignKey(
        Answer, on_delete=models.CASCADE, related_name="likes", verbose_name="Ответ"
    )
    value = models.SmallIntegerField(
        choices=VALUE_CHOICES, default=LIKE, verbose_name="Значение"
    )

    class Meta:
        unique_together = ("user", "answer")
        verbose_name = "Лайк ответа"
        verbose_name_plural = "Лайки ответов"

    def __str__(self):
        return f"{self.user.username} → ответ #{self.answer.pk}"
