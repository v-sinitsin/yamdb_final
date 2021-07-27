from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.http.response import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from . import serializers
from .filters import TitleFilter
from .models import Category, Comment, Genre, Review, Title
from .permissions import (IsAdminOrAccountOwner, IsAdminUserOrReadOnly,
                          isAdminUserModerator)
from .tokens import AccountActivationTokenGenerator

User = get_user_model()
token_generator = AccountActivationTokenGenerator()


@api_view(['POST'])
@permission_classes([AllowAny])
def send_confirmation_code(request):
    if request.method == 'POST':
        serializer = serializers.RegistrationDataSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data['email']
            username = serializer.data.get('username', email)
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email)
            except IntegrityError:
                user = User.objects.get(email=email)
            token = token_generator.make_token(user)
            send_mail(
                subject="Код для получения JWT-токена",
                message=token,
                from_email='api@yamdb.ru',
                recipient_list=(email,))
            return Response(serializer.data)
        return Response(serializer.errors)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_jwt_token(request):
    if request.method == 'POST':
        serializer = serializers.ConfirmationDataSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data['email']
            user = get_object_or_404(User, email=email)
            confirmation_code = serializer.data['confirmation_code']
            if not token_generator.check_token(user, confirmation_code):
                return JsonResponse({'token': 'Неверный код подтверждения!'})
            return JsonResponse({'token': str(RefreshToken.for_user(user))})


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAdminOrAccountOwner]
    lookup_field = 'username'
    search_fields = (lookup_field, )

    @action(methods=['get', 'patch'], detail=False)
    def me(self, request):
        user = self.request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg("reviews__score"))
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in ["POST", "PATCH"]:
            return serializers.TitleWriteSerializer
        return serializers.TitleReadSerializer


class CreateListDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    pass


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all().order_by("id")
    serializer_class = serializers.CategorySerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ["=name"]
    lookup_field = "slug"


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all().order_by("id")
    serializer_class = serializers.GenreSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ["=name"]
    lookup_field = "slug"


class ReviewsViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = serializers.ReviewSerializer
    permission_classes = (isAdminUserModerator,)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title_id=title)


class CommentsViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentsSerializer
    permission_classes = (isAdminUserModerator,)

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review_id=review)
