from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.title


RATE_CHOICES = [
    (1, '1 звезда'),
    (2, '2 звезды'),
    (3, '3 звезды'),
    (4, '4 звезды'),
    (5, '5 звезд'),
]


class Rating(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    value = models.PositiveIntegerField(choices=RATE_CHOICES, default=0)

    class Meta:
        unique_together = ('book', 'user')

