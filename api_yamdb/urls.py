from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from django.views.generic import TemplateView

urlpatterns = [
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
    path('api/v1/', include('api.urls')),
    path('admin/', admin.site.urls),
]
