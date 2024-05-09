from django.urls import path
from . import views

from courseplanner.users.views import (
    user_redirect_view,
    user_update_view,
    user_detail_view,
    user_plan_view,
    autocomplete_course_codes,
    generate_course_plan,

)

app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("plan/", view=user_plan_view, name="plan"),
    path("<str:username>/", view=user_detail_view, name="detail"),
    path("autocomplete_course_codes/", autocomplete_course_codes, name='autocomplete_course_codes'),
]
