import datetime
from typing import Any, override

from allauth.account.decorators import verified_email_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.generic import CreateView, DeleteView, UpdateView

from .forms import (
    AuthorForm,
    BookForm,
    BorrowOrReturnBookInstanceModelForm,
    CreateBookInstanceModelForm,
    RenewBookModelForm,
)
from .models import Author, Book, BookInstance


def index(request):
    """View function for home page of site."""

    num_books = Book.objects.count()
    num_instances = BookInstance.objects.count()

    num_instances_available = BookInstance.objects.filter(
        status__exact=BookInstance.LOAN_STATUS.Available
    ).count()

    num_authors = Author.objects.count()

    context = {
        "num_books": num_books,
        "num_instances": num_instances,
        "num_instances_available": num_instances_available,
        "num_authors": num_authors,
    }

    return render(request, "catalog/index.html", context=context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 5
    context_object_name = "book_list"


class BookDetailView(generic.DetailView):
    """Display an individual :model:`catalog.Book (does not hyperlink if in first line for views
    🙄)`

    Reachable via :view:`catalog.views.BookListView` by clicking on a book title.

    **Context**

    ``book``
        An instance of :model:`catalog.Book`.

    **Template:**

    :template:`catalog/book_detail.html` (this link only works properly if you have your app
    template dirs added to your TEMPLATES.DIRS)

    **Tags/Filters**

    - :tag:`book_detail_tags-run_extension`
    - :filter:`book_detail_filters-nonexistent_filter`
    """

    model = Book
    context_object_name = "book"

    @override
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # for hidden due_date field in form for borrowing book
        context["checkout_due_date"] = (
            datetime.date.today() + datetime.timedelta(weeks=3)
        ).isoformat()
        return context


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 5
    context_object_name = "author_list"
    queryset = Author.objects.all()


class AuthorDetailView(generic.DetailView):
    model = Author
    context_object_name = "author"


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""

    model = BookInstance
    context_object_name = "books_list"
    template_name = "catalog/borrowed_books.html"
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact=BookInstance.LOAN_STATUS.OnLoan)
            .order_by("due_back")
        )


class AllLoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    """All loaned books. Accessible only to users with the 'catalog.change_bookinstance'
    permission."""

    permission_required = "catalog.change_bookinstance"
    model = BookInstance
    context_object_name = "books_list"
    template_name = "catalog/borrowed_books.html"
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(
                book__title__icontains=self.request.GET.get("search", "")
            )
            .filter(status__exact=BookInstance.LOAN_STATUS.OnLoan)
            .order_by("due_back")
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["show_search"] = True
        context["show_renew_option"] = True
        return context


class RenewBookLibrarianModelView(PermissionRequiredMixin, UpdateView):
    model = BookInstance
    context_object_name = "book_instance"
    form_class = RenewBookModelForm
    template_name = "catalog/renew_book_librarian.html"
    permission_required = "catalog.change_bookinstance"
    success_url = reverse_lazy("catalog:all_borrowed")


class CheckoutOrReturnBookInstanceView(UpdateView):
    model = BookInstance
    context_object_name = "book_instance"
    form_class = BorrowOrReturnBookInstanceModelForm
    template_name = "catalog/checkout_or_return_book_instance.html"
    success_url = reverse_lazy("catalog:my_borrowed")


@method_decorator(verified_email_required, name="dispatch")
class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    permission_required = "catalog.add_author"
    form_class = AuthorForm

    @override
    def get_form(self, form_class: type[BaseModelForm] | None = None) -> BaseModelForm:
        form: AuthorForm = super().get_form(form_class)  # type: ignore
        form.helper.form_action = reverse("catalog:author_create")
        return form


@method_decorator(verified_email_required, name="dispatch")
class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    permission_required = "catalog.change_author"
    form_class = AuthorForm

    @override
    def get_form(self, form_class: type[BaseModelForm] | None = None) -> BaseModelForm:
        form: AuthorForm = super().get_form(form_class)  # type: ignore
        form.helper.form_action = reverse(
            "catalog:author_update", args=[str(form.instance.pk)]
        )
        return form


@method_decorator(verified_email_required, name="dispatch")
class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    # success_url required for DeleteView
    success_url = reverse_lazy("catalog:authors")
    permission_required = "catalog.delete_author"

    def form_valid(self, form):
        object = self.object  # type: ignore
        try:
            object.delete()
            return HttpResponseRedirect(self.success_url)  # type: ignore
        except Exception:
            return HttpResponseRedirect(
                reverse("catalog:author_delete", kwargs={"pk": object.pk})
            )


# always put a verification requirement here since creating new books allows for uploading cover images
# that aren't deleting a previous cover image (like the update page does), which is an attack vector
# to balloon object storage
@method_decorator(verified_email_required, name="dispatch")
class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    permission_required = "catalog.add_book"
    form_class = BookForm

    @override
    def get_form(self, form_class: type[BaseModelForm] | None = None) -> BaseModelForm:
        form: BookForm = super().get_form(form_class)  # type: ignore
        form.helper.form_action = reverse("catalog:book_create")
        return form


@method_decorator(verified_email_required, name="dispatch")
class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    permission_required = "catalog.change_book"
    form_class = BookForm

    @override
    def get_form(self, form_class: type[BaseModelForm] | None = None) -> BaseModelForm:
        form: BookForm = super().get_form(form_class)  # type: ignore
        form.helper.form_action = reverse(
            "catalog:book_update", args=[str(form.instance.pk)]
        )
        return form


@method_decorator(verified_email_required, name="dispatch")
class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy("catalog:books")
    permission_required = "catalog.delete_book"

    def form_valid(self, form):
        object = self.object  # type: ignore
        try:
            object.delete()
            return HttpResponseRedirect(self.success_url)  # type: ignore
        except Exception:
            return HttpResponseRedirect(
                reverse("catalog:book_delete", kwargs={"pk": object.pk})
            )


class BookInstanceCreateView(CreateView):
    model = BookInstance
    context_object_name = "book_instance"
    form_class = CreateBookInstanceModelForm
    template_name = "catalog/bookinstance_create.html"

    def get_success_url(self) -> str:
        return reverse("catalog:book_detail", kwargs={"pk": self.request.POST["book"]})


@method_decorator(verified_email_required, name="dispatch")
class BookInstanceDeleteView(DeleteView):
    model = BookInstance
    template_name = "catalog/bookinstance_delete.html"

    def get_object(self, queryset: QuerySet[Any] | None = None) -> BookInstance:
        self.object: BookInstance = super().get_object(queryset)  # type: ignore
        self.book = self.object.book.pk if self.object.book else None
        return self.object

    def get_success_url(self) -> str:
        return reverse("catalog:book_delete", kwargs={"pk": self.book})
