# ranieri_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('photographer/', include('photographer.urls', namespace='photographer')),
    path('public-galleries/', include('galleries_pub.urls', namespace='public_galleries')),
    path('galerias/', include('galleries.urls', namespace='galleries')),
    path('historia/', include('historia.urls', namespace='historia')),
    path('coral/', include('coral.urls', namespace='coral')),
    path('gremio/', include('gremio.urls', namespace='gremio')),
    path('simcozinha/', include('simcozinha.urls', namespace='simcozinha')),
    path('brindialogando/', include('brindialogando.urls', namespace='brindialogando')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

