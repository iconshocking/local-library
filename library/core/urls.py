from django.urls import include, path

from .views import LibraryMemberSignupView

urlpatterns = [
    path("accounts/signup/", LibraryMemberSignupView.as_view(), name="account_signup"),
    path("accounts/", include("allauth.urls")),
]
