"""testsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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

from django.urls import path, re_path
from django.shortcuts import render
from django.contrib.staticfiles.urls import urlpatterns as staticurlpatterns
from django.views.static import serve 
from api import urls as apiurls
from webapp_settings import DEBUG, STATIC_ROOT, WEBPACK_DEV_SERVER_URL, AUTH_CLIENT_ID, TITLE

# ONLY on debug fix for webpack fast refresh
from proxy.views import proxy_view
fix_web_pack_dev_server_urls = [] if not DEBUG else [re_path(r'^(?P<path>.*\..*hot-update\.((json)|(js)))$', lambda rq, path: proxy_view(rq, WEBPACK_DEV_SERVER_URL + path))]

urlpatterns = apiurls + staticurlpatterns + fix_web_pack_dev_server_urls + [
    # path('admin/', admin.site.urls),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': STATIC_ROOT}),
    re_path(r'^', lambda rq : render(rq, 'index.html', {'TITLE':TITLE,'AUTH_CLIENT_ID':AUTH_CLIENT_ID}))

]
