from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from ..utils.utils import get_graduation_years

class Term(models.TextChoices):
    FALL = 'Fall', _('Fall')
    SPRING = 'Spring', _('Spring')
    SUMMER = 'Summer', _('Summer')
    WINTER = 'Winter', _('Winter')

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

# The degree requirements consist of
# 1) General Education
# 2) Quantitative Requirements
# 3) Major (Curriculum) Requirements
# 4) University Elective Requirements (meet 120 credits)
class User(AbstractUser):

    name = models.CharField(_("Name of User"), blank=True, max_length=255) # redundant field
    GRAD_YEARS = get_graduation_years()
    expected_grad_year = models.IntegerField(choices=GRAD_YEARS, null=True)
    expected_grad_term = models.CharField(choices=Term.choices, null=True, max_length=6)

    file = models.FileField(upload_to='excel_files/', blank=True, null=True,
                            help_text="Upload your completed excel template. You may download a template on the home page.")

    def get_absolute_url(self):
        return reverse(
            "users:detail", kwargs={"username": self.username}
        )

class UserCourse(models.Model):
    GRAD_YEARS = get_graduation_years()
    year = models.IntegerField(choices=GRAD_YEARS, null=True)
    semester = models.CharField(choices=Term.choices, null=True, max_length=6)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    code = models.CharField(max_length=10, verbose_name=_('Course Code'))
    credits = models.IntegerField(verbose_name=_('Credits'))
    grade = models.CharField(max_length=2, choices=Grade.choices, verbose_name=_('Grade'), null=True)

    def __str__(self):
        return f'({self.credits}) {self.code} - {self.grade}'

class CourseTerm(models.Model):
    TERM_CHOICES = Term.choices

    name = models.CharField(max_length=20, choices=TERM_CHOICES, unique=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name=_('Course Code'))
    name = models.CharField(max_length=40)
    description = models.TextField()
    credits = models.PositiveIntegerField()
    offered = models.ManyToManyField(CourseTerm)
    prerequisites = models.ManyToManyField('self', related_name="prereqs", symmetrical=False, blank=True)
    corequisites = models.ManyToManyField('self', related_name="coreqs", symmetrical=False, blank=True)


    def __str__(self):
        return f'{self.code}'

class Curriculum(models.Model):
    PROGRAM_TYPES = [
        ('MAJ', 'Major'),
        ('MIN', 'Minor'),
        ('CERT', 'Certificate'),
        ('TRCK', 'Interest Track'),
    ]

    name = models.CharField(max_length=40)
    required_courses = models.ManyToManyField(Course)
    program_type = models.CharField(max_length=4, choices=PROGRAM_TYPES, default='MAJ')

    def __str__(self):
        return self.name