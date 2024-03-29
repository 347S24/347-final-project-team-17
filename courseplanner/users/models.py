from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Term(models.TextChoices):
    FALL = 'FALL', _('Fall')
    SPRING = 'SPRING', _('Spring')
    SUMMER = 'SUMMER', _('Summer')

class User(AbstractUser):

    # First Name and Last Name Do Not Cover Name Patterns
    # Around the Globe.
    name = models.CharField(
        _("Name of User"), blank=True, max_length=255
    )
    # GradYear
    expectedGraduationYear = models.IntegerField(
        default=timezone.now().year
        )
    # GradTerm
    expectedGraduationTerm = models.CharField(
        max_length=6,
        choices=Term.choices,
        default=Term.FALL,
    )

    def get_absolute_url(self):
        return reverse(
            "users:detail", kwargs={"username": self.username}
        )

