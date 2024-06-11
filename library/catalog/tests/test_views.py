import datetime
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import (
    Permission,
)
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from catalog.models import Author, Book, BookInstance, Genre, Language
from catalog.views import AllLoanedBooksListView


# views are tested using the django test Client, which is a dummy web browser with lots of useful
# information on the response, such as headers, templates used, redirects, etc.
#
# NOTE: views are usually tested as integration tests rather than unit tests, since they assert
# against the results of user behavior/situations
class AuthorListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_authors = 11

        for author_id in range(number_of_authors):
            Author.objects.create(
                first_name=f"Dominique {author_id}",
                last_name=f"Surname {author_id}",
            )

    # ONLY test the raw URL if it is important to the functionality of your site, which it shouldn't
    # be in most cases when using django's URLConf
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get("/catalog/authors/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse("catalog:authors"))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse("catalog:authors"))
        self.assertTemplateUsed(response, "catalog/author_list.html")

    # testing exact numbers is not useful since it makes the test brittle, so it is better to test
    # limits and thresholds
    def test_pagination_is_at_most_5(self):
        response = self.client.get(reverse("catalog:authors"))
        self.assertTrue(bool(response.context["is_paginated"]))
        self.assertLessEqual(len(response.context["author_list"]), 5)

    def test_pagination_sequential(self):
        authors = Author.objects.all()
        page = 1
        response = self.client.get(reverse("catalog:authors") + "?page=" + str(page))
        index = 0
        while index != len(authors):
            for i, author in enumerate(response.context["author_list"]):
                self.assertEqual(author, authors[i + index])
            index += len(response.context["author_list"])
            if response.context["page_obj"].has_next():
                page += 1
                response = self.client.get(
                    reverse("catalog:authors") + "?page=" + str(page)
                )
        self.assertFalse(response.context["page_obj"].has_next())


class TestUserTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        User = get_user_model()
        self.test_user1 = User.objects.create_user(  # type: ignore
            username="testuser1", password="1X<ISRUkw+tuK"
        )
        self.test_user1.raw_password = "1X<ISRUkw+tuK"
        self.test_user2 = User.objects.create_user(  # type: ignore
            username="testuser2", password="2HJ1vRV0Z&3iD"
        )
        self.test_user2.raw_password = "2HJ1vRV0Z&3iD"
        self.test_user1.save()
        self.test_user2.save()

        test_author = Author.objects.create(first_name="John", last_name="Smith")
        Genre.objects.create(name="Fantasy")
        test_language = Language.objects.create(name="English")
        self.test_book = Book.objects.create(
            title="Book Title",
            summary="My book summary",
            isbn="ABCDEFG",
            author=test_author,
            language=test_language,
        )

        # Direct assignment of many-to-many types not allowed
        genre_objects_for_book = Genre.objects.all()
        self.test_book.genre.set(genre_objects_for_book)
        self.test_book.save()


class LoanedBookInstancesByUserListViewTest(TestUserTestCase):
    def setUp(self):
        super().setUp()

        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = timezone.localtime() + datetime.timedelta(days=book_copy % 5)
            the_borrower = self.test_user1 if book_copy % 2 else self.test_user2
            BookInstance.objects.create(
                book=self.test_book,
                imprint="Unlikely Imprint, 2016",
                due_back=return_date,
                borrower=the_borrower,
                status=BookInstance.LOAN_STATUS.Maintenance,
            )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("catalog:my_borrowed"))
        self.assertRedirects(
            response,
            settings.LOGIN_URL + "?next=" + reverse("catalog:my_borrowed"),
        )

    # python only runs a method as a test if it starts with "test"
    def login_and_get_view_and_assert_logged_in(self):
        # can perform login using the client
        self.client.login(
            username=self.test_user1.username, password=self.test_user1.raw_password
        )
        response = self.client.get(reverse("catalog:my_borrowed"))
        self.assertEqual(
            str(response.context["user"]),
            str(self.test_user1),
        )
        self.assertEqual(response.status_code, 200)
        return response

    def test_logged_in_uses_correct_template(self):
        response = self.login_and_get_view_and_assert_logged_in()
        self.assertTemplateUsed(response, "catalog/all_loaned_books.html")

    def test_only_borrowed_books_in_list(self):
        response = self.login_and_get_view_and_assert_logged_in()
        # Check that initially we don't have any books in list (none on loan)
        self.assertTrue(AllLoanedBooksListView.context_object_name in response.context)
        self.assertEqual(
            len(response.context[AllLoanedBooksListView.context_object_name]),  # type: ignore
            0,
        )
        # Now change all books to be on loan
        BookInstance.objects.update(status=BookInstance.LOAN_STATUS.OnLoan)

        # Check that now we have borrowed books in the list
        response = self.client.get(reverse("catalog:my_borrowed"))
        self.assertTrue(AllLoanedBooksListView.context_object_name in response.context)
        # Confirm all books, at least on fist page, are on loan
        for bookitem in response.context[AllLoanedBooksListView.context_object_name]:  # type: ignore
            self.assertEqual(response.context["user"], bookitem.borrower)
            self.assertEqual(bookitem.status, BookInstance.LOAN_STATUS.OnLoan)

    def test_pages_ordered_by_due_date(self):
        # Change all books to be on loan
        BookInstance.objects.update(status=BookInstance.LOAN_STATUS.OnLoan)

        response = self.login_and_get_view_and_assert_logged_in()
        last_date = 0
        for book in response.context[AllLoanedBooksListView.context_object_name]:  # type: ignore
            if last_date == 0:
                last_date = book.due_back
            self.assertTrue(last_date <= book.due_back)
            last_date = book.due_back


class RenewBookInstancesViewTest(TestUserTestCase):
    def setUp(self):
        super().setUp()

        # Give test_user2 permission to renew books.
        permission = Permission.objects.get(codename="can_mark_returned")
        self.test_user2.user_permissions.add(permission)
        self.test_user2.save()

        def makeBook(borrower):
            return BookInstance.objects.create(
                book=self.test_book,
                imprint="Unlikely Imprint, 2016",
                due_back=datetime.date.today() + datetime.timedelta(days=5),
                borrower=self.test_user1,
                status=BookInstance.LOAN_STATUS.OnLoan,
            )

        self.test_bookinstance1 = makeBook(self.test_user1)
        self.test_bookinstance2 = makeBook(self.test_user2)

    def login_and_get_view(self, test_user, bookinstance):
        self.client.login(username=test_user.username, password=test_user.raw_password)
        return self.client.get(
            reverse(
                "catalog:renew_book_librarian",
                kwargs={"pk": bookinstance.pk},
            )
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(
            reverse(
                "catalog:renew_book_librarian",
                kwargs={"pk": self.test_bookinstance1.pk},
            )
        )
        self.assertRedirects(
            response,
            settings.LOGIN_URL
            + "?next="
            + reverse(
                "catalog:renew_book_librarian",
                kwargs={"pk": self.test_bookinstance1.pk},
            ),
        )

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        response = self.login_and_get_view(self.test_user1, self.test_bookinstance1)
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission_borrowed_book(self):
        response = self.login_and_get_view(self.test_user2, self.test_bookinstance2)
        # Check that it lets us login: this is our book and we have the right permissions.
        self.assertEqual(response.status_code, 200)

    def test_logged_in_with_permission_another_users_borrowed_book(self):
        response = self.login_and_get_view(self.test_user2, self.test_bookinstance1)
        # Check that it lets us login: we're a librarian, so we can view any user's book.
        self.assertEqual(response.status_code, 200)

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        test_uid = uuid.uuid4()
        self.client.login(
            username=self.test_user2.username, password=self.test_user2.raw_password
        )
        response = self.client.get(
            reverse("catalog:renew_book_librarian", kwargs={"pk": test_uid})
        )
        self.assertEqual(response.status_code, 404)

    def test_uses_correct_template(self):
        response = self.login_and_get_view(self.test_user2, self.test_bookinstance1)
        self.assertTemplateUsed(response, "catalog/renew_book_librarian.html")

    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        response = self.login_and_get_view(self.test_user2, self.test_bookinstance1)
        date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
        self.assertEqual(
            # get_initial_for_field will return the initial value whether it is set by the form or field
            response.context["form"].get_initial_for_field(
                response.context["form"].fields["renewal_date"], "renewal_date"
            ),
            date_3_weeks_in_future,
        )

    def test_redirects_to_all_borrowed_book_list_on_success(self):
        self.client.login(
            username=self.test_user2.username, password=self.test_user2.raw_password
        )
        valid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=2)
        response = self.client.post(
            reverse(
                "catalog:renew_book_librarian",
                kwargs={
                    "pk": self.test_bookinstance1.pk,
                },
            ),
            # post data that would be sent in a form
            {"renewal_date": valid_date_in_future},
        )
        self.assertRedirects(response, reverse("catalog:all_borrowed"))

