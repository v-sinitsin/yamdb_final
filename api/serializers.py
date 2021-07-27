from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Category, Comment, Genre, Review, Title

User = get_user_model()


class ChoiceField(serializers.ChoiceField):
    def to_representation(self, obj):
        return self._choices[obj]

    def to_internal_value(self, data):
        for key, val in self._choices.items():
            if val == data:
                return key
        self.fail('invalid_choice', input=data)


class UserSerializer(serializers.ModelSerializer):
    role = ChoiceField(choices=User.Role.choices)

    class Meta:
        fields = ('first_name', 'last_name', 'username',
                  'bio', 'email', 'role')
        model = User
        extra_kwargs = {
            'password': {'required': False},
            'email': {'required': True}
        }
        lookup_field = 'username'


class RegistrationDataSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(required=False)


class ConfirmationDataSerializer(serializers.Serializer):
    email = serializers.EmailField()
    confirmation_code = serializers.CharField()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Category
        lookup_field = "slug"


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Genre
        lookup_field = "slug"


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        fields = "__all__"
        model = Title


class TitleWriteSerializer(TitleReadSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(), slug_field="slug", many=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field="slug"
    )


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )
    title_id = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name',
    )

    class Meta:
        model = Review
        fields = '__all__'
        extra_kwargs = {'title_id': {'required': False}}

    def validate(self, data):
        title = self.context.get('view').kwargs.get('title_id')
        request = self.context.get('request')
        if (
            (request.method == request.method == 'POST')
            and Review.objects.filter(
                title_id=title, author=request.user
            ).exists()
        ):
            raise serializers.ValidationError('Score already exists')
        return data


class CommentsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date', 'review_id')
        model = Comment
        extra_kwargs = {
            'title_id': {'required': False},
            'review_id': {'required': False}
        }
