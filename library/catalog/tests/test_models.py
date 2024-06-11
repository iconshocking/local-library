from typing import override

from django.forms import ModelForm, ValidationError
from django.test import TestCase
from django.urls import reverse

from catalog.models import Author


# TestCase creates a new DB for the test class and runs each test in its own transaction. There are
# fast base classes if these features are not needed.
class YourTestClass(TestCase):
    @override
    @classmethod
    def setUpTestData(cls):
        # Run once to set up non-modified data for all class methods
        pass

    @override
    def setUp(self):
        # Run before every test method to set up clean data
        pass

    @override
    def tearDown(self) -> None:
        # Run after every test method to tear down resources.
        pass

    def test_false_is_false(self):
        self.assertFalse(False)


class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Author.objects.create(first_name="Big", last_name="Bob")
        cls.base_author = Author.objects.get(id=1)
        cls.form = AuthorModelTest.TestAuthorForm(instance=cls.base_author)

    # using a form to test labels instead of accessing '_meta' directly since it is not part of the
    # public API
    class TestAuthorForm(ModelForm):
        class Meta:
            model = Author
            fields = "__all__"

    def test_first_name_label(self):
        self.assertEqual(AuthorModelTest.form.fields["first_name"].label, "First name")

    def test_last_name_label(self):
        self.assertEqual(AuthorModelTest.form.fields["last_name"].label, "Last name")

    def test_date_of_birth_label(self):
        self.assertEqual(
            AuthorModelTest.form.fields["date_of_birth"].label, "Date of birth"
        )

    def test_date_of_death_label(self):
        self.assertEqual(AuthorModelTest.form.fields["date_of_death"].label, "Died")

    # testing behavior instead of implementation, so not testing
    # 'author_instance._meta.get_field("field_name").max_length' directly
    def test_first_name_max_length_100(self):
        def test():
            tooLongName = Author.objects.create(first_name="a" * 101, last_name="Todd")
            tooLongName.full_clean()

        self.assertRaises(ValidationError, test)

    def test_last_name_max_length_100(self):
        def test():
            tooLongName = Author.objects.create(first_name="Jim", last_name="a" * 101)
            tooLongName.full_clean()

        self.assertRaises(ValidationError, test)

    def test_object_name_is_last_name_comma_first_name(self):
        expected_object_name = f"{AuthorModelTest.base_author.last_name}, {AuthorModelTest.base_author.first_name}"
        self.assertEqual(str(AuthorModelTest.base_author), expected_object_name)

    def test_get_absolute_url(self):
        # This will also fail if the urlconf is not defined.
        self.assertEqual(
            AuthorModelTest.base_author.get_absolute_url(),
            reverse("catalog:author_detail", args=[1]),
        )
