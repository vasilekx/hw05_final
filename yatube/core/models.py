"""Core models configuration"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class CreatedModel(models.Model):
    """Абстрактная модель. Добавляет дату создания."""
    created = models.DateTimeField(
        _('Дата создания'),
        auto_now_add=True,
        help_text=_('Дата создания будет автоматически установлена '
                    'в текущую дату при создании')
    )

    class Meta:
        abstract = True
        ordering = ('-created',)
