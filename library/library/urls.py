"""
URL configuration for library project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.views import serve as serve_static
from django.urls import include, path
from django.views.decorators.cache import never_cache
from django.views.generic import RedirectView

urlpatterns = [
    # put this first to intercept the admin/doc/ URL
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    # default generated
    path("admin/", admin.site.urls),
    path("core/", include("core.urls")),
    path("catalog/", include("catalog.urls")),
    # "" instead of "/" since django always computes urls from the project root
    path("", RedirectView.as_view(url="/catalog/", permanent=True)),
    # metrics URL for prometheus scraping
    path("", include("django_prometheus.urls")),
    path("__reload__/", include("django_browser_reload.urls")),
]
if settings.DEBUG:
    # werid prependend slash in STATIC_URL once it gets set
    static_url = settings.STATIC_URL
    if static_url.startswith("/"):
        static_url = static_url[1:]

    urlpatterns += (
        # serve media files in development
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
        + [
            # serve static files in development that never cache to avoid development annoyances
            path(static_url + "<path:path>", never_cache(serve_static)),
        ]
        + [
            path("__debug__/", include("debug_toolbar.urls")),
        ]
    )
