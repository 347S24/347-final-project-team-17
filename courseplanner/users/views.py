from typing import Any
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import (
    DetailView,
    RedirectView,
    TemplateView,
)
from .forms import (
    CourseInputForm,
    UserUpdateForm,
    TranscriptUploadForm,
)
from .models import (
    UserCourse,
    Course,
)
from ..utils.utils import extract_course_info
from ..utils.course_util import generate_course_plan

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
        course_form = CourseInputForm(request.POST or None)
        user_courses = UserCourse.objects.filter(user=user)

        if "user_update_submit" in request.POST:
            if update_form.is_valid():
                update_form.save()
                return redirect(request.path_info)

        if "transcript_upload_submit" in request.POST:
            if transcript_form.is_valid():
                uploaded_file = transcript_form.cleaned_data['transcript']
                courses = extract_course_info(uploaded_file)
                UserCourse.objects.filter(user=user).delete()
                for course in courses:
                    UserCourse.objects.create(user=user, code=course[0], credits=course[1], grade=course[2])
                messages.success(request, f'{uploaded_file} uploaded successfully')

        if "course_input_submit" in request.POST:
            if course_form.is_valid():
                new_course = course_form.save(commit=False)
                new_course.user = user
                new_course.save()
                messages.success(request, "Course added successfully!")
                return redirect(request.path_info)

        if "remove_course_submit" in request.POST:
            course_id = request.POST.get("course_id")
            if course_id:
                UserCourse.objects.filter(id=course_id, user=user).delete()
                messages.success(request, "Course removed successfully!")
                return redirect(request.path_info)

        return self.render_to_response({'update_form': update_form, 'transcript_form': transcript_form, 'course_form': course_form, 'user_courses': user_courses})

    def get(self, request, *args, **kwargs):
        user = request.user
        update_form = UserUpdateForm(instance=request.user)
        transcript_form = TranscriptUploadForm
        course_form = CourseInputForm()
        user_courses = UserCourse.objects.filter(user=user)

        return self.render_to_response({'update_form': update_form, 'transcript_form': transcript_form, 'course_form': course_form, 'user_courses': user_courses})

    # Consider using this to reduce if branching?
    # def form_valid(self, form):
    #     if 'transcript-submit' in self.request.POST:
    #         form.save()
    #         return super().form_valid(form)
    #     else:
    #         return super().form_valid(form)

user_update_view = UserUpdateView.as_view()

# Autocomplete for UserUpdateView querying course codes.
def autocomplete_course_codes(request):
    term = request.GET.get('term')
    courses = Course.objects.filter(name__icontains=term)
    course_codes = [course.code for course in courses]
    return JsonResponse(course_codes, safe=False)
                  
class UserPlanView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/plan.html'

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     user = self.request.user
    #     semesters, graph = generate_course_plan(user.curriculums.all(), 16)
    #     context['semesters'] = semesters
    #     context['graph'] = graph
    #     return context
    
    def post(self, request, *args, **kwargs):
        user = self.request.user
        semesters, graph = generate_course_plan(user.curriculums.all(), 16)
        return render(request, self.template_name, {'semesters': semesters, 'graph': graph})

user_plan_view = UserPlanView.as_view()

class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse(
            "users:detail",
            kwargs={"username": self.request.user.username},
        )


user_redirect_view = UserRedirectView.as_view()

