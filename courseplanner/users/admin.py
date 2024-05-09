from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.utils.html import format_html

from courseplanner.users.forms import (
    UserChangeForm,
    UserCreationForm,
)
from courseplanner.users.models import (
    UserCourse,
    CourseTerm,
    Course,
    CourseGroup,
    Requirement,
    Curriculum,
)

User = get_user_model()

@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (
        ("User", {"fields": ("name", "expected_grad_year", "expected_grad_term")}),
    ) + auth_admin.UserAdmin.fieldsets
    list_display = ["username", "name", "is_superuser", "expected_grad_year", "expected_grad_term"]
    search_fields = ["name", "expected_grad_year", "expected_grad_term"]

@admin.register(UserCourse)
class UserCourseAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'credits', 'grade']
    search_fields = ['code']

admin.site.register(CourseTerm)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):

    # Allows the ManyToMany 'offered' field to be represented in the list display
    def terms_to_string(self, obj):
        return ", ".join([term.name for term in obj.offered.all()])
    terms_to_string.short_description = 'Offered Terms'

    list_display = ['code', 'name', 'description', 'terms_to_string', 'credits']
    search_fields = ['code', 'name']
    ordering = ['code']
    filter_horizontal = ('prerequisites','corequisites','offered')

class CourseInline(admin.StackedInline):
    model = Course
    extra = 1

class CourseGroupInline(admin.TabularInline):
    model = CourseGroup
    filter_horizontal = ['requirements']
    extra = 1

class RequirementInline(admin.TabularInline):
    model = Curriculum.requirements.through
    extra = 1

@admin.register(Requirement)
class RequirementAdmin(admin.ModelAdmin):
    inlines = [CourseInline, CourseGroupInline]

@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = ['name', 'program_type', 'representation']
    filter_horizontal = ['requirements']

    def representation(self, obj):

        print(obj.display())
        return format_html(obj.display().replace('\n', '<br/>').replace('\t', '|---'))



    representation.short_description = 'Visualization'
    representation.allow_tags = True