from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    
    #apps
    path('LightWeather/', include('weather.urls')),
    path('api/v1/', include('rest_api.urls')),
    
    #external applications
    path('captcha/', include('captcha.urls')),
]
    


if settings.DEBUG == 'True':
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
