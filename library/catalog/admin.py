from django.contrib import admin
from django.http import HttpRequest

from .models import Author, Book, BookInstance, Genre, Language


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "display_genre")

    # cannot display many-to-many field in list_display because of performance on large DBs, so we
    # create a callable (maybe not recommended, but using for example)
    @admin.display(description="Genre")
    def display_genre(self, obj):
        return ", ".join([genre.name for genre in obj.genre.all()[:3]])

    class BooksInstanceInline(admin.TabularInline):
        model = BookInstance

        def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
            return False

        can_delete = False
        extra = 0

    inlines = [BooksInstanceInline]


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "date_of_birth", "date_of_death")
    fields = ["first_name", "last_name", ("date_of_birth", "date_of_death")]

    class BookInline(admin.TabularInline):
        model = Book
        extra = 0
        can_delete = False

        def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
            return False

    inlines = [BookInline]


admin.site.register(Genre)
admin.site.register(Language)


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ("status", "due_back", "borrower", "book", "id")
    list_filter = (
        "status",
        "due_back",
    )
    fieldsets = (
        (None, {"fields": ("book", "imprint", "id")}),
        ("Availability", {"fields": ("status", "due_back", "borrower")}),
    )
