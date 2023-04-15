from .models import Book, Rating
from .forms import RatingForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from book_rating import models
from django.views.generic import DetailView
from django.contrib import messages


class CustomPaginator:
    @staticmethod
    def paginate(object_list: any, per_page=5, page_number=1):
        paginator_instance = Paginator(object_list=object_list, per_page=per_page)
        try:
            page = paginator_instance.page(number=page_number)
        except PageNotAnInteger:
            page = paginator_instance.page(number=1)
        except EmptyPage:
            page = paginator_instance.page(number=paginator_instance.num_pages)
        return page


def book_create(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        context = {}
        return render(request, 'add_book.html', context=context)
    elif request.method == "POST":
        print("request: ", request)
        print("request.POST: ", request.POST)
        print("request.GET: ", request.GET)
        print("request.META: ", request.META)

        title = request.POST.get('title', None)
        description = request.POST.get('description', "")
        author = request.POST.get('author', "")
        book = models.Book.objects.create(
            title=title,
            description=description,
            author=author,
        )
        return redirect(reverse('book_list', args=()))


def book_list(request: HttpRequest) -> HttpResponse:
    books = models.Book.objects.all()

    selected_page_number_books = request.GET.get('page', 1)
    selected_limit_objects_per_page_books = request.GET.get('limit', 3)
    if request.method == "POST":
        selected_page_number_books = 1
        selected_limit_objects_per_page_books = 9999
        search_by_title_books = request.POST.get('search', None)
        if search_by_title_books is not None:
            books = books.filter(title__contains=str(search_by_title_books))
        filter_by_user_books = request.POST.get('filter', None)
        if filter_by_user_books is not None:
            books = books.filter(user=User.objects.get(username=filter_by_user_books))
    page_books = CustomPaginator.paginate(
        object_list=books, per_page=selected_limit_objects_per_page_books, page_number=selected_page_number_books
    )

    context = {"page_books": page_books, "users": User.objects.all()}
    return render(request, 'book_list.html', context=context)


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    rating = None
    user = request.user
    if user.is_authenticated:
        try:
            rating = Rating.objects.filter(book=book, user=request.user).first()
        except Rating.DoesNotExist:
            pass

    rating_stars = ''
    if rating:
        for i in range(1, 11):
            if i <= rating.rating:
                rating_stars += '★'
            else:
                rating_stars += '☆'

    context = {
        'book': book,
        'rating': rating,
        'rating_stars': rating_stars,
    }
    return render(request, 'book_detail.html', context)


def book_delete(request: HttpRequest, pk: int) -> HttpResponse:
    book = models.Book.objects.get(id=pk)
    book.delete()
    return redirect(reverse('book_list', args=()))


def book_pk_view(request: HttpRequest, pk: int) -> HttpResponse:
    if request.method == "GET":
        context = {}
        return render(request, 'book_detail.html', context=context)
    context = {}
    return render(request, 'book_list.html', context=context)


def rate_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    user = request.user
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.cleaned_data['rating']
            try:
                rating_obj = Rating.objects.get(book=book, user=user)
                rating_obj.rating = rating
                rating_obj.save()
            except Rating.DoesNotExist:
                rating_obj = Rating.objects.create(book=book, user=user, rating=rating)
            return redirect('book_detail', pk=book.pk)
    else:
        form = RatingForm()
    return render(request, 'rate_book.html', {'form': form, 'book': book})


class BookDetailView(DetailView):
    model = Book
    template_name = 'book_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.get_object()
        user = self.request.user

        if user.is_authenticated:
            book_rating = get_object_or_404(Rating, book=book, user=user)
            context['user_rating'] = book_rating.rating

        return context


