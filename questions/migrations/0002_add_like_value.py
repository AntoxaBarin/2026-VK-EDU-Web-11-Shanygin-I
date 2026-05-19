from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("questions", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="questionlike",
            name="value",
            field=models.SmallIntegerField(
                choices=[(1, "Like"), (-1, "Dislike")],
                default=1,
                verbose_name="Значение",
            ),
        ),
        migrations.AddField(
            model_name="answerlike",
            name="value",
            field=models.SmallIntegerField(
                choices=[(1, "Like"), (-1, "Dislike")],
                default=1,
                verbose_name="Значение",
            ),
        ),
    ]
