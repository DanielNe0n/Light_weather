from django.http import JsonResponse
from django.contrib import messages

from weather.models import City

from decouple import config
import requests


API_KEY = config('WEATHER_API')

class CityRequestMaster():
    """
        class that provides the main functionality
        for using the OpenWeather API.            
                                                  """
    
    def returning_cities(request):
        city_temp = {} # So that it is easier to unpack the data for js later

        #Use session or model
        if request.user.is_authenticated:
            cities = City.objects.filter(user=request.user)
        else:
            cities = request.session.get('cities', [])


        if cities:
            #if session/list
            if type(cities) == list:
                for city in cities:
                    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric'
                    resp = requests.get(url)
                    print(url)
                    
                    weather_data = resp.json()
                    city_temp[city] = weather_data

            #if model/queryset
            else:
                for city in cities:
                    url = f'https://api.openweathermap.org/data/2.5/weather?q={city.name}&appid={API_KEY}&units=metric'
                    resp = requests.get(url)
                    print(url)
                    
                    weather_data = resp.json()
                    city_temp[city.name] = weather_data
            #return unpack cities data 
            return JsonResponse({'status':200, **city_temp})
                                

        return JsonResponse({'status':'there are no data'})

    def addding_city(request):
        #Use session or model
        if request.user.is_authenticated:
            cities = City.objects.filter(user=request.user)
        else:
            cities = request.session.get('cities', [])

        #Getting the city from the <input> and remove the extra space
        city = request.POST.get('entered_city').strip() 
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric'
        resp = requests.get(url)

        #Checking whether such a city exists
        if resp.status_code == 200:
            if not request.user.is_authenticated:
                #If such a city exists, we check whether it is already in the session
                if city not in cities:
                    if len(cities) > 3:   
                        cities.pop(0)

                    cities.append(city)
                    request.session['cities'] = cities
                else:
                    messages.error(request, 'City already added')
            else:
                #If such a city exists, we check whether it is already in the model
                if not cities.filter(name=city).exists():
                    if cities.count() > 3:  
                        cities.first().delete()

                    City.objects.create(user=request.user, name=city)
                else:
                    messages.error(request, 'City already added')

            #Taking data from OpenWeather in js format
            weather_data = resp.json()
            return JsonResponse({'status':200, **weather_data})

        else:
            print("status 400")
            messages.error(request, 'City not found')
            return JsonResponse({'status':resp.status_code})


    def get_city(data):
        #Checking whether one city is provided (with request.POST)
        if type(data) == str: 
            url = f'https://api.openweathermap.org/data/2.5/weather?q={data}&appid={API_KEY}&units=metric'
            resp = requests.get(url=url)
            return [resp.json(), resp.status_code]
        
        #Or many are transferred (queryset)
        else:
            cities_temp = {}
            for city in data: 
                url = f'https://api.openweathermap.org/data/2.5/weather?q={city.name}&appid={API_KEY}&units=metric'
                resp = requests.get(url)
                if resp.status_code == 200:
                    weather_data = resp.json()
                else:
                    weather_data = {'error':resp.status_code}
                cities_temp[city.name] = weather_data
            return cities_temp

def is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'
