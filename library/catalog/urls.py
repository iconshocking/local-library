from django.urls import path, re_path

from . import views

app_name = __package__

urlpatterns = [
    path("", views.index, name="index"),
    path("books/", views.BookListView.as_view(), name="books"),
    # 're_path()' performs match using regexp (takes a string argument though)
    # - NOTE: capture groups without names are passed as positional arguments to the view function
    re_path(r"^book/(?P<pk>\d+)/$", views.BookDetailView.as_view(), name="book_detail"),
    # equivalent to former line, except adding the optional kwargs argument
    # - NOTE: conflict between kwargs and captured argument names will prefer the kwargs value
    path(
        "book/<int:pk>/nonregexp/",
        views.book_detail_view_fun,
        {"extra_info": "some goodies"},
        name="book_detail_nonregexp",
    ),
    path("authors/", views.AuthorListView.as_view(), name="authors"),
    path("authors/<int:pk>/", views.AuthorDetailView.as_view(), name="author_detail"),
    path("mybooks/", views.LoanedBooksByUserListView.as_view(), name="my_borrowed"),
    path("loanedbooks/", views.AllLoanedBooksListView.as_view(), name="all_borrowed"),
    path(
        "book/<uuid:pk>/renew/",
        views.RenewBookLibrarianView.as_view(),
        name="renew_book_librarian",
    ),
    path(
        "book/<uuid:pk>/renew/function/",
        views.renew_book_librarian,
        name="renew_book_librarian_function",
    ),
    path(
        "book/<uuid:pk>/renew/model/",
        views.RenewBookLibrarianView.as_view(),
        name="renew_book_librarian_model",
    ),
    path(
        "book/<int:pk>/update/",
        views.BookUpdate.as_view(),
        name="book_update",
    ),
    path(
        "book/<int:pk>/delete/",
        views.BookDelete.as_view(),
        name="book_delete",
    ),
    path(
        "book/create/",
        views.BookCreate.as_view(),
        name="book_create",
    ),
    path(
        "author/<int:pk>/update/",
        views.AuthorUpdate.as_view(),
        name="author_update",
    ),
    path(
        "author/<int:pk>/delete/",
        views.AuthorDelete.as_view(),
        name="author_delete",
    ),
    path(
        "author/create/",
        views.AuthorCreate.as_view(),
        name="author_create",
    ),
    path("session-playground/", views.sessionPlayground, name="session_playground"),
]
