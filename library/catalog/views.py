import datetime
from typing import Any, override

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models.base import Model as Model
from django.forms import BaseModelForm
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic import CreateView, DeleteView, UpdateView

from .forms import CrispyBookForm, RenewBookForm, RenewBookModelForm
from .models import Author, Book, BookInstance, Genre


# function-based view
def index(request):
    """View function for home page of site."""

    num_books = Book.objects.all().count()  # all() is implied by default.
    num_instances = BookInstance.objects.count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(
        status__exact=BookInstance.LOAN_STATUS.Available
    ).count()

    num_authors = Author.objects.count()

    num_books_containing_memor = Book.objects.filter(title__icontains="memor").count()
    num_genre_containing_trash: int = Genre.objects.filter(
        name__icontains="trash"
    ).count()

    context = {
        "num_books": num_books,
        "num_instances": num_instances,
        "num_instances_available": num_instances_available,
        "num_authors": num_authors,
        "num_books_containing_memor": num_books_containing_memor,
        "num_genre_containing_trash": num_genre_containing_trash,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, "catalog/index.html", context=context)


# class-based view
class BookListView(generic.ListView):
    model = Book
    paginate_by = 2
    # your own name for the list as a template variable; defaults to 'model_name_list' (can always
    # access 'object_list' as well)
    context_object_name = "book_list"
    # can alternatively override get_queryset()
    queryset = Book.objects.all().order_by("-title")  # can override default ordering
    # Specify your own template name/location with 'template_name' (defaults to looking in
    # <app_name>/templates/<app_name>/<model_name>_list.html)

    # this is the context data that will be passed to the template
    @override
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["some_data"] = "This is just some data"
        # can attach the view object to the context for arbitrary access in the template
        context["view"] = self
        context["viewfunction"] = lambda: self.lazymethod("Hello from a lambda!")
        return context

    def lazymethod(self, string):
        return string + " (called lazily from the template)"


class BookDetailView(generic.DetailView):
    """Display an individual :model:`catalog.Book (does not hyperlink if in first line for views
    🙄)`

    Reachable via :view:`catalog.views.BookListView` by clicking on a book title.

    **Context**

    ``book``
        An instance of :model:`catalog.Book`.

    **Template:**

    :template:`catalog/book_detail.html` (this link only works properly if you have your app
    template dirs added to your TEMPLATES.DIRS 🙄)

    **Tags/Filters**

    - :tag:`book_detail_tags-run_extension`
    - :filter:`book_detail_filters-nonexistent_filter`
    """

    model = Book
    # defaults to 'model_name' (can always access 'object' as well)
    context_object_name = "book"
    # Can specify your own template name/location (defaults to looking in
    # <app_name>/templates/<app_name>/<model_name>_detail.html)


# equivalent function-based view (note: how we have to handle the 404 ourselves since we
# don't get the default handling from the class)
def book_detail_view_fun(request, pk, **kwargs):
    # same as querying the model, excepting Book.DoesNotExist error and raising Http404 when needed
    book = get_object_or_404(Book, pk=pk)
    return render(request, "catalog/book_detail.html", context={"book": book})


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 2
    context_object_name = "author_list"
    queryset = Author.objects.all()


class AuthorDetailView(generic.DetailView):
    model = Author
    context_object_name = "author"


def sessionPlayground(request: HttpRequest):
    if request.GET.get("reset") == "1":
        request.session.clear()

    num_visits = request.session.get("num_visits", 0) + 1
    request.session["num_visits"] = num_visits

    extras = request.session.get("extras", {})
    if not extras:
        request.session["extras"] = extras
    extras["time"] = datetime.datetime.now().isoformat()
    # nested changes are not saved to the session DB automatically, so upadate .modified
    request.session["extras"]["time"] = datetime.datetime.now().isoformat()
    request.session.modified = True

    return render(
        request,
        "catalog/session_playground.html",
        context={"num_visits": num_visits},
    )


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""

    model = BookInstance
    context_object_name = "books_list"
    template_name = "catalog/all_loaned_books.html"
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact=BookInstance.LOAN_STATUS.OnLoan)
            .order_by("due_back")
        )


class AllLoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    """All loaned books. Accessible only to users with the 'catalog.can_mark_returned'
    permission."""

    permission_required = "catalog.can_mark_returned"
    model = BookInstance
    context_object_name = "books_list"
    template_name = "catalog/all_loaned_books.html"
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
        return context


# FormView:
# - renders unbound form on GET
# - the bound form with errors on POST if validation fails
# - redirects on POST if validation succeeds
class RenewBookLibrarianView(PermissionRequiredMixin, generic.FormView):
    form_class = RenewBookForm
    template_name = "catalog/renew_book_librarian.html"
    # can set 'initial' to override the initial values for the form
    permission_required = "catalog.can_mark_returned"
    # lazy util allows us to use a callable here since the URLConf is still being defined at the
    # time this view class will be created; otherwise we need to define get_success_url()
    success_url = reverse_lazy("catalog:all_borrowed")

    # override instead of __init__() since it does NOT receive the request or URLConf args/kwargs
    # (ONLY the kwargs passed to the .as_view() function in the URLConf route definition)
    @override
    def setup(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
        super().setup(request, *args, **kwargs)
        self.book_instance = get_object_or_404(BookInstance, pk=self.kwargs["pk"])

    @override
    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["book_instance"] = self.book_instance
        return kwargs

    @override
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # 'form' was passed to context in super call
        context["book_instance"] = self.book_instance
        return context

    @override
    def form_valid(self, form):
        self.book_instance.due_back = form.cleaned_data["renewal_date"]
        self.book_instance.save()
        return super().form_valid(form)


# equivalent ModelForm view
class RenewBookLibrarianModelView(PermissionRequiredMixin, UpdateView):
    form_class = RenewBookModelForm
    template_name = "catalog/renew_book_librarian.html"
    permission_required = "catalog.can_mark_returned"
    success_url = reverse_lazy("catalog:all_borrowed")


# equivalent function view
@login_required
@permission_required("catalog.can_mark_returned", raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == "POST":
        # Create a form instance and populate it with data from the request (binding)
        form = RenewBookForm(book_instance, data=request.POST)
        # Check if the form is valid
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data["renewal_date"]
            book_instance.save()
            # redirect to a new URL
            return HttpResponseRedirect(reverse("catalog:all_borrowed"))

    # If this is a GET (or any other method) create the default form
    else:
        proposed_renewal_date: datetime.date = (
            datetime.date.today() + datetime.timedelta(weeks=3)
        )
        form = RenewBookForm(
            book_instance, initial={"renewal_date": proposed_renewal_date}
        )
    context = {
        "form": form,
        "book_instance": book_instance,
    }
    return render(request, "catalog/renew_book_librarian_alt.html", context)


# Create/UpdateViews defaults:
# - success_url: the model's get_absolute_url()
# - form_class: ModelForm
# - template_name: 'app_name/model_name_form.html'
class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ["first_name", "last_name", "date_of_birth", "date_of_death"]
    initial = {"date_of_death": "11/11/2023"}
    permission_required = "catalog.add_author"


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = "__all__"
    permission_required = "catalog.change_author"


# Create/UpdateViews defaults:
# - template_name: 'app_name/model_name_confirm_delete.html'
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


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    permission_required = "catalog.add_book"
    form_class = CrispyBookForm

    @override
    def get_form(self, form_class: type[BaseModelForm] | None = None) -> BaseModelForm:
        form: CrispyBookForm = super().get_form(form_class)  # type: ignore
        form.helper.form_action = reverse("catalog:book_create")
        return form


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    permission_required = "catalog.change_book"
    form_class = CrispyBookForm

    @override
    def get_form(self, form_class: type[BaseModelForm] | None = None) -> BaseModelForm:
        form: CrispyBookForm = super().get_form(form_class)  # type: ignore
        form.helper.form_action = reverse(
            "catalog:book_update", args=[str(form.instance.pk)]
        )
        return form


# Create/UpdateViews defaults:
# - template_name: 'app_name/model_name_confirm_delete.html'
class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    # success_url required for DeleteView
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
