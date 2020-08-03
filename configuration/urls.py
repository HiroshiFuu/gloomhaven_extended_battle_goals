from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include, url
from django.urls import path
from django.urls import re_path
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views

from django.contrib.sites.models import Site
from allauth.account.models import EmailAddress
admin.site.unregister(Site)
admin.site.unregister(EmailAddress)

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Medical Analysis API",
      default_version="v1",
      description="For Indonesia Hopsitals",
      contact=openapi.Contact(email="hao.feng@hpe.com"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),

    # User management
    url(r'^accounts/', include('allauth.urls')),

    # Your stuff: custom urls includes go here
    url(r'^swagger-ui/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^v1/swagger-ui/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui-v1'),
    re_path('api/v1/', include('backend.urls', namespace='v1')),
    # url(r'^api/v2/swagger-ui/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui-v2'),
    # re_path('api/v2/', include('backend.urls', namespace='v2')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    # urlpatterns += [
    #     url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
    #     url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
    #     url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
    #     url(r'^500/$', default_views.server_error),
    # ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
                          url(r'^__debug__/', include(debug_toolbar.urls)),
                      ] + urlpatterns
