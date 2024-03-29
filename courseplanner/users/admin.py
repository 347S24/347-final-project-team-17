from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from courseplanner.users.forms import (
    UserChangeForm,
    UserCreationForm,
)

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (
        ("User", {"fields": ("name", "expectedGraduationYear", "expectedGraduationTerm")}),
    ) + auth_admin.UserAdmin.fieldsets
    list_display = ["username", "name", "is_superuser", "expectedGraduationYear", "expectedGraduationTerm"]
    search_fields = ["name", "expectedGraduationYear", "expectedGraduationTerm"]
