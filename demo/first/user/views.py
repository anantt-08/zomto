#from django.shortcuts import render
#from .serializers import UserSerializer
#from rest_framework.views import APIView
#from rest_framework.response import Response
#from rest_framework import authentication, permissions
#from django.contrib.auth.models import User
#import random
#from rest_framework.permissions import IsAuthenticated,AllowAny
  

from hashlib import new
from xmlrpc.client import ResponseError
from rest_framework import permissions, generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth import login
from .serializers import (CartSerializer, CitySerializer, CreateUserSerializer,
                          UserSerializer)
from .models import *
from django.shortcuts import get_object_or_404
from django.db.models import Q
import requests
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken

import random
import datetime


def send_otp(phone):
    if phone:
        otp = random.randint(999, 9999)
    return otp


class ValidatePhoneSendOTP(APIView):
    '''
    This class view takes phone number and if it doesn't exists already then it sends otp for
    first coming phone numbers'''

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone')
        if phone_number:
            phone = str(phone_number)
            user = User.objects.filter(phone__iexact = phone)
            if user.exists() == False:
                Temp_data = {'phone': phone}
                user = User.create(phone)
            
            otp = send_otp(phone)
            print(phone, otp)
            if otp:
                otp = str(otp)
                count = 0
                old = PhoneOTP.objects.filter(phone__iexact = phone)
                if old.exists():
                    oldOtp = old.first()
                    oldOtp.count = oldOtp.count + 1
                    oldOtp.otp = otp
                    oldOtp.save()
                
                else:
                    count = count + 1
            
                    PhoneOTP.objects.create(
                            phone =  phone, 
                            otp =   otp,
                            count = count
    
                            )
                if count > 7:
                    return Response({
                        'status' : False, 
                            'detail' : 'Maximum otp limits reached. Kindly support our customer care or try with different number'
                    })
                    
              
                return Response({
                    'status': True, 'detail': 'Otp has been sent successfully.'
                })
        else:
            return Response({
                'status': 'False', 'detail' : "Phone number required. Please do a POST request."
            })


class CustomAuthToken(ObtainAuthToken):
    def getUserAuthToken(self,user):
        print("token : ")
        token, created = Token.objects.get_or_create(user=user)
        if not created:
                # update the created time of the token to keep it valid
                token.created = datetime.datetime.utcnow()
                token.save()
        print("token : ",  token)
        if(token != None):
            return token.key
        return None

class ValidateOTP(APIView):
    '''
    If you have received otp, post a request with phone and that otp and you will be redirected to set the password
    
    '''

    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone', False)
        otp_sent   = request.data.get('otp', False)

        if phone and otp_sent:
            user = User.objects.filter(phone = phone)
            old = PhoneOTP.objects.filter(phone = phone)
            if old.exists():
                old = old.first()
                otp = old.otp
                if str(otp) == str(otp_sent):
                    old.logged = True
                    old.save()
                    customAuthToken = CustomAuthToken();
                    userToken = customAuthToken.getUserAuthToken(user[0])
                    return Response({
                        'status' : True, 
                        'detail' : 'OTP matched, kindly proceed!',
                        'token' : userToken
                    })
                else:
                    return Response({
                        'status' : False, 
                        'detail' : 'OTP incorrect, please try again'
                    })
            else:
                return Response({
                    'status' : False,
                    'detail' : 'Phone not recognised. Kindly request a new otp with this number'
                })


        else:
            return Response({
                'status' : 'False',
                'detail' : 'Either phone or otp was not recieved in Post request'
            })


class Register(APIView):

    '''Takes phone and a password and creates a new user only if otp was verified and phone is new'''

    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone', False)
        password = request.data.get('password', False)

        if phone and password:
            phone = str(phone)
            user = User.objects.filter(phone__iexact = phone)
            if user.exists():
                return Response({'status': False, 'detail': 'Phone Number already have account associated. Kindly try forgot password'})
            else:
                old = PhoneOTP.objects.filter(phone__iexact = phone)
                if old.exists():
                    old = old.first()
                    if old.logged:
                        Temp_data = {'phone': phone, 'password': password }

                        serializer = CreateUserSerializer(data=Temp_data)
                        serializer.is_valid(raise_exception=True)
                        user = serializer.save()
                        user.save()

                        old.delete()
                        return Response({
                            'status' : True, 
                            'detail' : 'Congrts, user has been created successfully.'
                        })

                    else:
                        return Response({
                            'status': False,
                            'detail': 'Your otp was not verified earlier. Please go back and verify otp'

                        })
                else:
                    return Response({
                    'status' : False,
                    'detail' : 'Phone number not recognised. Kindly request a new otp with this number'
                })
                    




        else:
            return Response({
                'status' : 'False',
                'detail' : 'Either phone or password was not recieved in Post request'
            })


class CityService(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cityList = City.objects.all()
        serializedData = CitySerializer(cityList, many = True)
        return Response(serializedData.data)


class UserCityUpdate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request,  *args, **kwargs):
        city = request.data.get('city', False)
        cityObject = City.objects.filter(id = city)
        if( not cityObject):
            return Response("City not found",status.HTTP_400_BAD_REQUEST)
        cityObject = cityObject.first()
        user = request.user
        user.city = cityObject
        user.save()
        return Response(UserSerializer(user).data)


class CartService(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cartList = Cart.objects.all()
        return Response(CartSerializer(cartList, many = True).data)

    def post(self, request,  *args, **kwargs):
        cartId = request.data.get('id', False)
        #if cartItem is not present, then insert it, else update it
        cartItem = Cart.objects.get(id = cartId)
        data = CartSerializer(instance=cartItem, data=request.data)
    
        if data.is_valid():
            data.save()
            return Response(data.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)




        


                

