from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from courseplanner.users.forms import (
    UserChangeForm,
    UserCreationForm,
)
from courseplanner.users.models import (
    UserCourse,
    Course,
    CourseTerm,
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

admin.site.register(CourseTerm)

@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = ['name', 'program_type']
    filter_horizontal = ['required_courses']