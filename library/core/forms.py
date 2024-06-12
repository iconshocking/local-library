from typing import Any, override

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms


class CrispyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "form-id"
        self.helper.form_class = "form-class"
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", "Submit"))
        self.helper.form_error_title = "Form Errors"

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
