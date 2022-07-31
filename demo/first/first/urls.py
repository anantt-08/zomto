"""first URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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

from django.urls import path, include, re_path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token

from user.views import ValidatePhoneSendOTP
from user.views import *

urlpatterns = [

    re_path(r'^admin/', admin.site.urls),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('sendOtp', ValidatePhoneSendOTP.as_view(), name="send_otp"),
    path('verifyOtp', ValidateOTP.as_view(), name="verify_otp"),
    path('city', CityService.as_view(), name="city"),
    path('update-city', UserCityUpdate.as_view(), name="update-city"),
    path('cart', CartService.as_view(), name="cart"),
]

