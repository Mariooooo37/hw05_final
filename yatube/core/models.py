from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class CreatedModel(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    pub_date = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        abstract = True
        default_related_name = 'posts'
