import datetime

from django.test import SimpleTestCase
from django.utils import timezone

from catalog.forms import RenewBookForm


# SimpleTestCase doesn't allow DB access, so it is faster than TestCase (though it can be enabled
# manually)
class RenewBookFormTest(SimpleTestCase):
    def test_renew_form_date_field_label(self):
        form = RenewBookForm()
        self.assertTrue(
            form.fields["renewal_date"].label is None
            or form.fields["renewal_date"].label == "Renewal date"
        )

    def test_renew_form_date_field_help_text(self):
        form = RenewBookForm()
        self.assertEqual(
            form.fields["renewal_date"].help_text,
            "Enter a date between now and 4 weeks (default 3).",
        )

    def test_renew_form_date_in_past(self):
        date = datetime.date.today() - datetime.timedelta(days=1)
        form = RenewBookForm(data={"renewal_date": date})
        self.assertFalse(form.is_valid())

    def test_renew_form_date_too_far_in_future(self):
        date = (
            datetime.date.today()
            + datetime.timedelta(weeks=4)
            + datetime.timedelta(days=1)
        )
        form = RenewBookForm(data={"renewal_date": date})
        self.assertFalse(form.is_valid())

    def test_renew_form_date_today(self):
        date = datetime.date.today()
        form = RenewBookForm(data={"renewal_date": date})
        self.assertTrue(form.is_valid())

    def test_renew_form_date_max(self):
        date = timezone.localtime() + datetime.timedelta(weeks=4)
        form = RenewBookForm(data={"renewal_date": date})
        self.assertTrue(form.is_valid())

    def test_form_invalid_renewal_date_past(self):
        form = RenewBookForm(
            data={"renewal_date": datetime.date.today() - datetime.timedelta(weeks=1)}
        )
        self.assertFormError(form, "renewal_date", "Invalid date - renewal in past")  # type: ignore

    def test_form_invalid_renewal_date_future(self):
        form = RenewBookForm(
            data={"renewal_date": datetime.date.today() + datetime.timedelta(weeks=5)}
        )
        self.assertFormError(  # type: ignore
            form, "renewal_date", "Invalid date - renewal more than 4 weeks ahead"
        )
