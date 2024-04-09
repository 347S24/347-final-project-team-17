from django import forms as form
from django.contrib.auth import get_user_model, forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from .models import Term, UserCourse
from ..utils.utils import get_graduation_years



User = get_user_model()

class UserChangeForm(forms.UserChangeForm):

    expectedGraduationYear = form.TypedChoiceField(
        coerce=int,
        choices=get_graduation_years(),
        empty_value=None
    )

    expectedGraduationTerm = form.ChoiceField(choices=Term.choices)

    class Meta(forms.UserChangeForm.Meta):
        model = User
        fields = '__all__' # can customize to include fields

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        self.fields['expectedGraduationYear'].choices = get_graduation_years()


class UserCreationForm(forms.UserCreationForm):

    expectedGraduationYear = form.TypedChoiceField(
        coerce=int,
        choices=get_graduation_years(),
        empty_value=None
    )

    expectedGraduationTerm = form.ChoiceField(choices=Term.choices)

    error_message = forms.UserCreationForm.error_messages.update(
        {
            "duplicate_username": _(
                "This username has already been taken."
            )
        }
    )

    class Meta(forms.UserCreationForm.Meta):
        model = User
        fields = ('username', 'expectedGraduationYear', 'expectedGraduationTerm')  # Include the fields you want on the signup form

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['expectedGraduationYear'].choices = get_graduation_years()

    def clean_username(self):
        username = self.cleaned_data["username"]

        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username

        raise ValidationError(
            self.error_messages["duplicate_username"]
        )

class UserUpdateForm(form.ModelForm):
    class Meta:
        model = User
        fields = ['expectedGraduationTerm', 'expectedGraduationYear', 'file']
        labels = {
            'expectedGraduationTerm' : 'Expected Graduation Term',
            'expectedGraduationYear' : 'Expected Graduation Year',
            'file' : 'Upload Template'
        }

class TranscriptUploadForm(form.Form):
    transcript = form.FileField(label='(optional) Upload transcript here. This will overwrite current courses.',
                                validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
                                required=False)


class CourseInputForm(form.ModelForm):
        class Meta:
            model = UserCourse
            fields = ['code', 'credits', 'grade']
            labels = {
                'code': 'Course',
                'credits': 'Credits',
                'grade': 'Grade',
            }
