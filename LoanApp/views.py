from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail  import send_mail
from django.conf import settings
from .models import User,OTPVerification
from django.utils.timezone import now
from datetime import timedelta
import datetime
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import make_password
from .serializers import *
from .models import*
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

class RegsiterUserView(APIView):
  
    permission_classes = [AllowAny]
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
    
    permission_classes=[AllowAny]
    def post(self, request):
        print("Received OTP verification request!")  
        email = request.data.get("email")
        otp_code = request.data.get("otp_code")

        if not email or not otp_code:
            return Response({"status": "error", "message": "Email and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            print(f"User found: {user.email}")  

            otp_record = OTPVerification.objects.filter(user=user, otp_code=otp_code, is_used=False).first()

            if not otp_record:
                return Response({"status": "error", "message": "Invalid OTP or OTP expired"}, status=status.HTTP_400_BAD_REQUEST)

            # Check if OTP has expired
            if otp_record.expires_at < now():
                return Response({"status": "error", "message": "OTP has expired"}, status=status.HTTP_400_BAD_REQUEST)

            # Mark OTP as used
            otp_record.is_used = True
            otp_record.save()
            
            user.email_verified = True
            user.save()

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            print(f"🔹 Generated Access Token: {access_token}")
            print(f"🔹 Generated Refresh Token: {refresh_token}")


            return Response({
                "status": "success",
                "message": "OTP verified successfully!",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "role":user.role,
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            print("User not found!")  
            return Response({"status": "error", "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
class LoanCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            print("Headers received:", request.headers)
            print("Auth:", request.auth)
            print("User:", request.user)
            user = request.user  # Extract the authenticated user
            if not user:
                return Response({"message": "User not found"}, status=status.HTTP_401_UNAUTHORIZED)

            amount = float(request.data.get("amount", 0))
            tenure = float(request.data.get("tenure", 0))
            interest_rate = float(request.data.get("interest_rate", 0))

            if not amount or not tenure or interest_rate is None:
                return Response({"message": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

            # Generate loan_id
            last_loan = Loan.objects.order_by('-loan_id').first()
            loan_id = f"LOAN{int(last_loan.loan_id.replace('LOAN', '')) + 1:03}" if last_loan else "LOAN001"

            # Set start date and end date
            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=tenure * 30)

            # Calculate EMI
            if interest_rate == 0:
                emi = round(amount / tenure, 2)
            else:
                monthly_rate = interest_rate / (12 * 100)
                emi = round((amount * monthly_rate * (1 + monthly_rate) ** tenure) / ((1 + monthly_rate) ** tenure - 1), 2)

            # Save Loan with User
            loan = Loan.objects.create(
                loan_id=loan_id,
                user=user,  # Associate with the authenticated user
                amount=amount,
                tenure=tenure,
                interest_rate=interest_rate,
                start_date=start_date,
                end_date=end_date
            )

            return Response({
                "status": "success",
                "data": {
                    "loan_id": loan.loan_id,
                    "amount": amount,
                    "tenure": tenure,
                    "interest_rate": f"{interest_rate}% yearly",
                    "monthly_installment": emi,
                    "payment_schedule": [{"installment_no": i + 1, "due_date": (start_date + timedelta(days=30 * (i + 1))).strftime("%Y-%m-%d"), "amount": emi} for i in range(int(tenure))]
                }
            }, status=status.HTTP_201_CREATED)

        except ValueError:
            return Response({"message": "Invalid input data"}, status=status.HTTP_400_BAD_REQUEST)
        