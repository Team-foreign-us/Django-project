"""
URL configuration for Foreign_us project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from django.views.generic import TemplateView

from Foreign_us.views import MainView, AboutUsView, MainHelpersListAPI

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('member/', include('member.urls')),
    path('mypage/', include('mypage.urls')),
    path('profile/', include('profilepage.urls')),
    path('lesson/', include('lesson.urls')),
    path('event/', include('event.urls')),
    path('helpers/', include('helpers.urls')),
    path('notice/', include('notice.urls')),
    path('administrator/', include('administrator.urls')),
    path('', MainView.as_view()),
    path('about-us/', TemplateView.as_view(template_name='about_us/about_us.html')),
    path('list/<int:page>', MainHelpersListAPI.as_view(), name='helpers_list'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)