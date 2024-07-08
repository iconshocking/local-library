import datetime

from core.forms import CrispyForm
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Book, BookInstance


class RenewBookModelForm(forms.ModelForm):
    def clean_due_back(self):
        data = self.cleaned_data["due_back"]

        if data < datetime.date.today():
            raise forms.ValidationError(_("Invalid date - renewal in past"))

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

# form is not meant for visual; just easy way to update the book instance
class BorrowOrReturnBookInstanceModelForm(forms.ModelForm):
    class Meta:
        model = BookInstance
        fields = ["borrower", "due_back", "status"]

class CreateBookInstanceModelForm(forms.ModelForm):
    class Meta:
        model = BookInstance
        fields = ["book"]

class BookForm(CrispyForm):
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
