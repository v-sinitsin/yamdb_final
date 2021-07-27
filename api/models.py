from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import validate_date, validate_username_length


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = 'user', 'user'
        MODERATOR = 'moderator', 'moderator'
        ADMIN = 'admin', 'admin'

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        max_length=150, unique=True,
        validators=[validate_username_length, username_validator])
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=9,
        choices=Role.choices,
        default=Role.USER)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = User.Role.ADMIN
        super().save(*args, **kwargs)


class Category(models.Model):
    name = models.TextField('Название', blank=False, max_length=150)
    slug = models.SlugField('slug', blank=False, unique=True, db_index=True)

    def __str__(self):
        return self.name[0:10]


class Genre(models.Model):
    name = models.TextField('Название', blank=False, max_length=150)
    slug = models.SlugField('slug', blank=False, unique=True, db_index=True)

    def __str__(self):
        return self.name[0:10]


class Title(models.Model):
    name = models.TextField(
        'Название',
        blank=False,
        max_length=200,
        db_index=True
    )
    year = models.IntegerField('Год', blank=True, validators=[validate_date])
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='titles',
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        db_index=True,
        related_name='titles',
        verbose_name='Жанр'
    )
    description = models.CharField(
        'Описание',
        max_length=200,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name[0:10]


class Review(models.Model):
    title_id = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        null=True,
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        null=True,
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, blank=True
    )


class Comment(models.Model):
    review_id = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        null=True
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        null=True
    )
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
