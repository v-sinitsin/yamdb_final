from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('users', views.UserViewSet, basename='user')
router.register('titles', views.TitleViewSet, basename='title')
router.register('categories', views.CategoryViewSet, basename='category')
router.register('genres', views.GenreViewSet, basename='genre')
router.register(
    r'titles/(?P<title_id>[\d]+)/reviews',
    views.ReviewsViewSet,
    basename='review'
)
router.register(
    r'titles/(?P<title_id>[\d]+)/reviews/(?P<review_id>[\d]+)/comments',
    views.CommentsViewSet,
    basename='comment'
)

urlpatterns = [
    path('auth/email/', views.send_confirmation_code),
    path('auth/token/', views.send_jwt_token),
    path('', include(router.urls))
]
