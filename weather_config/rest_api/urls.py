from django.urls import path
from . import views


app_name = 'rest'


urlpatterns = [
    path('info/', views.info_page, name='info_page'),
    path('all/', views.CityList.as_view(), name='all_cities'),
    path('retrieve/', views.CityRetrieve.as_view(), name='retrieve_city'),
]
