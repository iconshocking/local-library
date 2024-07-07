from django.urls import path

from . import views

app_name = __package__

urlpatterns = [
    path("", views.index, name="index"),
    path("books/", views.BookListView.as_view(), name="books"),
    path("book/<int:pk>/", views.BookDetailView.as_view(), name="book_detail"),
    path("authors/", views.AuthorListView.as_view(), name="authors"),
    path("authors/<int:pk>/", views.AuthorDetailView.as_view(), name="author_detail"),
    path("mybooks/", views.LoanedBooksByUserListView.as_view(), name="my_borrowed"),
    path("loanedbooks/", views.AllLoanedBooksListView.as_view(), name="all_borrowed"),
    path(
        "book/<uuid:pk>/renew/",
        views.RenewBookLibrarianModelView.as_view(),
        name="renew_book_librarian",
    ),
    path(
        "update-checkout/<uuid:pk>/",
        views.CheckoutOrReturnBookInstanceView.as_view(),
        name="checkout_or_return_book_instance",
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
]
