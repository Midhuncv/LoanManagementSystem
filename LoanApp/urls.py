from django.urls import path
from .views import *

urlpatterns = [
    
    
    path('RegsiterUserView/',RegsiterUserView.as_view(),name='RegsiterUserView'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('LoanCreateView/',LoanCreateView.as_view(),name='LoanCreateView'),
    path('Render/',Render.as_view(),name='Render')
]
