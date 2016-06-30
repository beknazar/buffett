from django.conf import settings
from django.conf.urls import url
from django.views.static import serve

from views import *


urlpatterns = [
    url(r'^$', index, name='home'),
]
urlpatterns += [
    url(r'^static/(?P<path>(js|css|less|img|components|bower_components)/.+)$',
        serve, {'document_root': settings.STATIC_ROOT}),
]
