from django import forms as form
from django.contrib.auth import get_user_model, forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from allauth.account.forms import SignupForm
from .models import Term, UserCourse
from ..utils.utils import get_graduation_years
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field



User = get_user_model()

class UserChangeForm(forms.UserChangeForm):

    expected_grad_year = form.TypedChoiceField(
        coerce=int,
        choices=get_graduation_years(),
        empty_value=None
    )

    expected_grad_term = form.ChoiceField(choices=Term.choices)

    class Meta(forms.UserChangeForm.Meta):
        model = User
        fields = '__all__' # can customize to include fields

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        self.fields['expected_grad_year'].choices = get_graduation_years()


class UserCreationForm(forms.UserCreationForm):

    expected_grad_year = form.TypedChoiceField(
        coerce=int,
        choices=get_graduation_years(),
        empty_value=None
    )

    expected_grad_term = form.ChoiceField(choices=Term.choices)

    error_message = forms.UserCreationForm.error_messages.update(
        {
            "duplicate_username": _(
                "This username has already been taken."
            )
        }
    )

    class Meta(forms.UserCreationForm.Meta):
        model = User
        fields = ('username', 'expected_grad_year', 'expected_grad_term')  # Include the fields you want on the signup form

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['expected_grad_year'].choices = get_graduation_years()

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
        fields = ['expected_grad_term', 'expected_grad_year', 'file', 'curriculums']
        labels = {
            'file' : 'Upload Template',
            'curriculums' : 'Plan(s) of Study',
        }
        widgets = {
            'curriculums': form.SelectMultiple(attrs={'class': 'form-control'}),
        }

class TranscriptUploadForm(form.Form):
    transcript = form.FileField(
        label='Upload Transcript',
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        required=False,
        help_text="This will overwrite current courses."
    )


class CourseInputForm(form.ModelForm):
        
    # Customize crispy forms layout to include 
    def __init__(self, *args, **kwargs):
        super(CourseInputForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.layout = Layout(
            Field('code', css_class='autocomplete'),
            Field('credits'),
            Field('grade'),
        )

    class Meta:
        model = UserCourse
        fields = ['code', 'credits', 'grade']
        labels = {
            'code': 'Course Code',
            'credits': 'Credits',
            'grade': 'Grade',
        }

class CustomSignupForm(SignupForm):
    POSSIBLE_YEARS = get_graduation_years()
    expected_grad_year = form.ChoiceField(
        choices=[('', 'Select Year')] + POSSIBLE_YEARS,
        required=True,
    )
    expected_grad_term = form.ChoiceField(choices=[('', 'Select Term')] + Term.choices)

    def clean_expected_grad_year(self):
        value = self.cleaned_data.get('expected_grad_year')
        if value == '':
            return None  # Skip validation for blank value
        return value

    def clean_expected_grad_term(self):
        value = self.cleaned_data.get('expected_grad_term')
        if value == '':
            return None  # Skip validation for blank value
        return value

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.expected_grad_year = self.cleaned_data['expected_grad_year']
        user.save()
        return user