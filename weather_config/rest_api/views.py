from django.contrib.auth.decorators import login_required
from django.forms import model_to_dict
from django.shortcuts import render

from rest_framework.exceptions import APIException, AuthenticationFailed
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import views

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from weather.utils import CityRequestMaster
from weather.models import City


#about API
@login_required()
def info_page(request):
    token, created = Token.objects.get_or_create(user=request.user)
    return render(request, 'rest_api/rest_info_page.html', {'token':token.key})



class CityList(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')

        if auth_header:
            print(auth_header)
        cities = City.objects.filter(user=self.request.user)

        if cities:
            resp_instance = CityRequestMaster
            json_data = resp_instance.get_city(cities)
            if type(json_data) == dict:
                return Response({**json_data})
        raise APIException('Not haven\'t cities')
    

    def post(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        cities = City.objects.filter(user=self.request.user)

        if token is None:
            raise AuthenticationFailed('Token is missing')

        city = self.request.data['city']

        resp_instance = CityRequestMaster
        resp = resp_instance.get_city(city)

        if resp[1] != 200:
            return Response({'Error':'City not found'})

        if cities.filter(name=city).exists():
            return Response({'Error':'This city already exists'})

        elif resp[1] == 200:
            if cities.count() >= 4:
                cities.first().delete()
            post_new = City.objects.create(user=self.request.user, name=city)
            return Response({'data':model_to_dict(post_new)})
        

class CityRetrieve(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')

        if token is None:
            raise AuthenticationFailed('Token is missing')

        city = self.request.data['city']
        
        resp_instance = CityRequestMaster
        resp = resp_instance.get_city(city)

        if resp[1] == 200:
            return Response({**dict(resp[0])})
        else:
            return Response({'Error':'City not found'})