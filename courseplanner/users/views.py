from typing import Any
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import (
    DetailView,
    RedirectView,
    TemplateView,
)
from .forms import (
    UserUpdateForm,
    TranscriptUploadForm,
)
from .models import (
    UserCourse
)
from ..utils.utils import extract_course_info
from django.contrib import messages

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    # These Next Two Lines Tell the View to Index
    #   Lookups by Username
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_courses = UserCourse.objects.filter(user=self.request.user)
        context['user_courses'] = user_courses
        return context

user_detail_view = UserDetailView.as_view()

class UserUpdateView(LoginRequiredMixin, TemplateView):
    
    template_name = "users/user_form.html"

    def post(self, request, *args, **kwargs):
        user = request.user
        update_form = UserUpdateForm(request.POST, request.FILES, instance=user)
        transcript_form = TranscriptUploadForm(request.POST, request.FILES)

        if "user_update_submit" in request.POST:
            if update_form.is_valid():
                update_form.save()
                return redirect(request.path_info)

        if "transcript_upload_submit" in request.POST:
            messages.warning(request, "Attempting to validate")
            if transcript_form.is_valid():
                uploaded_file = transcript_form.cleaned_data['transcript']
                courses = extract_course_info(uploaded_file)
                UserCourse.objects.filter(user=user).delete()
                for course in courses:
                    UserCourse.objects.create(user=user, code=course[0], credits=course[1], grade=course[2])
                messages.success(request, uploaded_file)

        messages.success(request, "Success!")
        return self.render_to_response({'update_form': update_form, 'transcript_form': transcript_form})

    def get(self, request, *args, **kwargs):
        update_form = UserUpdateForm(instance=request.user)
        transcript_form = TranscriptUploadForm
        return self.render_to_response({'update_form': update_form, 'transcript_form': transcript_form})

    # Consider using this to reduce if branching?
    # def form_valid(self, form):
    #     if 'transcript-submit' in self.request.POST:
    #         form.save()
    #         return super().form_valid(form)
    #     else:
    #         return super().form_valid(form)

user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse(
            "users:detail",
            kwargs={"username": self.request.user.username},
        )


user_redirect_view = UserRedirectView.as_view()
