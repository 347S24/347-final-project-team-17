import random
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
    curriculums = models.ManyToManyField('Curriculum')

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

# Abstract class for Course, CourseGroup, and possibly others
class Requirement(models.Model):

    def get_satisfiable_subset(self):
        if hasattr(self, 'course'):
            return self.course.get_satisfiable_subset() 
        elif hasattr(self, 'coursegroup'):
            return self.coursegroup.get_satisfiable_subset() 
        raise NotImplementedError("This class is abstract -- method needs to be implemented in the child class.")
    
    def get_credits(self):
        if hasattr(self, 'course'):
            return self.course.get_credits() 
        elif hasattr(self, 'coursegroup'):
            return self.coursegroup.get_credits() 
        raise NotImplementedError("This class is abstract -- method needs to be implemented in the child class.")

    def __str__(self):
        if hasattr(self, 'course'):
            return str(self.course)  
        elif hasattr(self, 'coursegroup'):
            return str(self.coursegroup)
        else:
            return super().__str__()
        
    # def __repr__(self) -> str:
    #     return str(self)
    
# Represents a single course
class Course(Requirement):

    code = models.CharField(max_length=10, unique=True, verbose_name=_('Course Code'))
    credits = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=40)
    description = models.TextField()
    offered = models.ManyToManyField(CourseTerm)
    prerequisites = models.ManyToManyField('self', related_name="prereqs", symmetrical=False, blank=True)
    corequisites = models.ManyToManyField('self', related_name="coreqs", symmetrical=False, blank=True)

    def get_satisfiable_subset(self) -> set:
        return set([self])
    
    def get_credits(self) -> int:
        return self.credits

    def __str__(self):
        return f'{self.code}\n'

# Represents a collection of courses with a minimum credit requirement in order to be satisfied
class CourseGroup(Requirement):

    requirements = models.ManyToManyField(Requirement, related_name='requirements')
    minimum_credits = models.PositiveSmallIntegerField()

    def get_satisfiable_subset(self) -> set:
        accumulated_credits = 0
        satisfiable_subset = []
        all_reqs = list(self.requirements.all())

        # Keep selecting random requirements until credit constraint is satisfied
        while accumulated_credits < self.get_credits():
            # Error check here... "is requirement_set empty?"
            random_requirement = random.choice(all_reqs)
            all_reqs.remove(random_requirement)
            satisfiable_subset += random_requirement.get_satisfiable_subset()
            accumulated_credits += random_requirement.get_credits()

        return set(satisfiable_subset)
    
    def get_credits(self) -> int:
        return self.minimum_credits
    
    def __str__(self):
        result = f"CourseGroup ({self.minimum_credits} credits)\n"
        for requirement in self.requirements.all():
            result += f"\t{requirement}"
        return result

class Curriculum(models.Model):
    PROGRAM_TYPES = [
        ('MAJ', 'Major'),
        ('MIN', 'Minor'),
        ('CERT', 'Certificate'),
        ('TRCK', 'Interest Track'),
    ]

    name = models.CharField(max_length=40)
    requirements = models.ManyToManyField(Requirement)
    program_type = models.CharField(max_length=4, choices=PROGRAM_TYPES, default='MAJ')

    def display(self):
        result = ""
        for requirement in self.requirements.all():
            result += f"{requirement}"
        return result

    def __str__(self):
        return f'{self.name} | {self.get_program_type_display()}' 