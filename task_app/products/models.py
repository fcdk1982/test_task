from django.contrib.auth.models import User
from django.db import models

from django.db.models import CharField
from django.db.models.functions import Length

# add custom lookup with length
CharField.register_lookup(Length)


class Product(models.Model):
    """
    class for product model
    """
    name = models.CharField(
        verbose_name='Назва продукту',
        max_length=100,
    )
    price = models.DecimalField(
        verbose_name='Ціна продукту',
        max_digits=5,
        decimal_places=2
    )
    create_by = models.ForeignKey(
        User, null=True,
        related_name='products',
        verbose_name='Кліент',
        on_delete=models.SET_NULL,
    )
    create_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = 'Products'
