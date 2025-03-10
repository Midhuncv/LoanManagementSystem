from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail  import send_mail
from django.conf import settings
from .models import User,OTPVerification
from django.utils.timezone import now
from datetime import timedelta
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import make_password
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

class RegsiterUserView(APIView):
    permission_classes =  [AllowAny]
    
    def post(self,request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create(
                email = serializer.validated_data['email'],
                password = make_password(serializer.validated_data['password']),
                email_verified = False
            )
            
            otp = OTPVerification.objects.create(user=user)
        # Send OTP via Email
            subject = "Your OTP Code"
            message = f"Hello, your OTP code is: {otp.otp_code}. It expires in 5 minutes."
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

            return Response({"status": "success", "message": "OTP sent to email!"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]  # ✅ Allow unauthenticated users

    def post(self, request):
        print("Received OTP verification request!")  # ✅ Debugging log
        email = request.data.get("email")
        otp_code = request.data.get("otp_code")

        if not email or not otp_code:
            return Response({"status": "error", "message": "Email and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            print(f"User found: {user.email}")  # ✅ Debugging log

            otp_record = OTPVerification.objects.filter(user=user, otp_code=otp_code, is_used=False).first()

            if not otp_record:
                return Response({"status": "error", "message": "Invalid OTP or OTP expired"}, status=status.HTTP_400_BAD_REQUEST)

            # Check if OTP has expired
            if otp_record.expires_at < now():
                return Response({"status": "error", "message": "OTP has expired"}, status=status.HTTP_400_BAD_REQUEST)

            # Mark OTP as used
            otp_record.is_used = True
            otp_record.save()

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            print(f"Tokens generated: access={access_token}, refresh={refresh_token}")  # ✅ Debugging log

            return Response({
                "status": "success",
                "message": "OTP verified successfully!",
                "access_token": access_token,
                "refresh_token": refresh_token
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            print("User not found!")  # ✅ Debugging log
            return Response({"status": "error", "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
                