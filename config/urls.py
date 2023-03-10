from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    # API (v1)
    url(r'^auth/', include('v1.accounts.urls')),
    url(r'^album/', include('v1.albums.urls')),

    # Core
    url(r'^admin/', admin.site.urls),
    url(r'^docs/', include_docs_urls(title='Gallery')),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
