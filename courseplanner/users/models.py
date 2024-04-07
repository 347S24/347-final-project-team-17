from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from ..utils.utils import get_graduation_years

class Term(models.TextChoices):
    FALL = 'FALL', _('Fall')
    SPRING = 'SPRING', _('Spring')
    SUMMER = 'SUMMER', _('Summer')
    WINTER = 'WINTER', _('Winter')

class Grade(models.TextChoices):
    A = 'A', _('A')
    A_MINUS = 'A-', _('A-')
    B_PLUS = 'B+', _('B+')
    B = 'B', _('B')
    B_MINUS = 'B-', _('B-')
    C_PLUS = 'C+', _('C+')
    C = 'C', _('C')
    C_MINUS = 'C-', _('C-')
    D_PLUS = 'D+', _('D+')
    D = 'D', _('D')
    F = 'F', _('F')
    PASS = 'P', _('Pass')
    WITHDRAW = 'W', _('Withdraw')
    CREDIT = 'CR', _('Credit')
    INCOMPLETE = 'I', _('Incomplete')
    WITHDRAWFAIL = 'WF', _('Withdraw Fail')
    WITHDRAWPASS = 'WP', _('Withdraw Pass')

class User(AbstractUser):

    name = models.CharField(
        _("Name of User"), blank=True, max_length=255
    )
    # GradYear
    POSSIBLE_YEARS = get_graduation_years()
    expectedGraduationYear = models.IntegerField(
        choices=POSSIBLE_YEARS, 
        null=True,
        blank=True,)
    # GradTerm
    expectedGraduationTerm = models.CharField(
        max_length=6,
        choices=Term.choices,
        null=True,
        blank=True,
    )

    file = models.FileField(upload_to='excel_files/', blank=True, null=True)



    def get_absolute_url(self):
        return reverse(
            "users:detail", kwargs={"username": self.username}
        )

class UserCourse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    code = models.CharField(max_length=10, verbose_name=_('Course Code'))
    credits = models.IntegerField(verbose_name=_('Credits'))
    grade = models.CharField(max_length=2, choices=Grade.choices, verbose_name=_('Grade'), null=True)

    def __str__(self):
        return f'({self.credits}) {self.code} - {self.grade}'
