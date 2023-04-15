from django.urls import path
from . import views
from .views import BookDetailView, rate_book

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('<int:pk>/', views.book_detail, name='book_detail'),
    path('book/<int:pk>/', views.book_delete, name='book_delete'),
    path('<int:pk>/', BookDetailView.as_view(), name='book_detail'),
    path('rate_book/<int:pk>/', views.rate_book, name='rate_book'),
    path('add/', views.book_create, name='book_create'),
]