import datetime
from typing import Any, override

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Book, BookInstance


class RenewBookForm(forms.Form):
    # Not using book instance, but practicing passing an argument to a form
    def __init__(self, book_instance=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.book_key = book_instance

    renewal_date = forms.DateField(
        initial=datetime.date.today() + datetime.timedelta(weeks=3),
        help_text="Enter a date between now and 4 weeks (default 3).",
        widget=forms.widgets.Input(attrs={"type": "date"}),
    )

    def clean_renewal_date(self):
        print("I GOT THE BOOK KEY", self.book_key)
        data = self.cleaned_data["renewal_date"]

        # Check if a date is not in the past.
        if data < datetime.date.today():
            raise forms.ValidationError(_("Invalid date - renewal in past"))

        # Check if a date is in the allowed range (+4 weeks from today).
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise forms.ValidationError(
                _("Invalid date - renewal more than 4 weeks ahead")
            )

        return data


# same form using ModelForm
class RenewBookModelForm(forms.ModelForm):
    def clean_due_back(self):
        data = self.cleaned_data["due_back"]

        # Check if a date is not in the past.
        if data < datetime.date.today():
            raise forms.ValidationError(_("Invalid date - renewal in past"))

        # Check if a date is in the allowed range (+4 weeks from today).
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise forms.ValidationError(
                _("Invalid date - renewal more than 4 weeks ahead")
            )

        return data

    class Meta:
        model = BookInstance
        fields = ["due_back"]
        labels = {"due_back": _("Renewal date")}
        help_texts = {
            "due_back": _("Enter a date between now and 4 weeks (default 3).")
        }
        widgets = {"due_back": forms.widgets.Input(attrs={"type": "date"})}


class CrispyBookForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        # ID and class can be whatever you want
        self.helper.form_id = "book-form"
        self.helper.form_class = "crispy-book-form"
        self.helper.form_method = "post"
        # adds submit button
        self.helper.add_input(Submit("submit", "Submit"))
        self.helper.form_error_title = "Form Errors"

    class Meta:
        model = Book
        fields = [
            "title",
            "author",
            "summary",
            "isbn",
            "genre",
            "language",
            "cover_image",
        ]

    def clean_summary(self):
        data = self.cleaned_data["summary"]
        if data.lower().startswith("summary"):
            raise forms.ValidationError(_("Summary cannot start with 'Summary'"))
        return data

    def clean_isbn(self):
        data = self.cleaned_data["isbn"]
        if len(data) < 13:
            raise forms.ValidationError(_("ISBN must be 13 characters"))
        return data

    @override
    def clean(self) -> dict[str, Any]:
        # for accessibility, this puts all errors at the top of the form, in addition to next to
        # their respective inputs
        error_list = []
        for key, error in self.errors.items():
            if key is not None:
                error_list.append(error)

        for error in error_list:
            self.add_error(None, error)

        return super().clean()
