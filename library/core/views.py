from typing import override

from allauth.account.forms import SignupForm
from allauth.account.views import SignupView
from django.contrib.auth.models import Group

from .models import User


class LibraryMemberSignupView(SignupView):
    class LibraryMemberSignupForm(SignupForm):
        @override
        def save(self, request):
            user: User = super().save(request)
            # gets users the correct permissions on signup
            user.groups.add(Group.objects.get(name="Library Members"))
            user.save()
            return user

    form_class = LibraryMemberSignupForm
