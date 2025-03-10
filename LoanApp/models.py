from django.db import  models
import uuid
from django.contrib.auth.hashers import make_password,check_password
import random
from django.utils.timezone import now
from datetime import timedelta



class User(models.Model):
    ADMIN = 'admin'
    USER='user'
    
    ROLE_CHOICES = [
        (ADMIN,'Admin'),
        (USER,'User')
    ]
    id= models.UUIDField(default=uuid.uuid4,primary_key=True,editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=10,choices=ROLE_CHOICES,default=USER)
    email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin= models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
    def set_password(self,raw_password):
        self.password = make_password(raw_password)
        
    def check_password(self,raw_password):
        return check_password(raw_password,self.password)
    
    
class OTPVerification(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otps")
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)  

    def save(self, *args, **kwargs):
        if not self.otp_code:
            self.otp_code = str(random.randint(100000, 999999))
        if not self.expires_at:
            self.expires_at = now() + timedelta(minutes=5)
        super().save(*args, **kwargs)

    def is_valid(self):
        return not self.is_used and now() < self.expires_at

    def __str__(self):
        return f"OTP for {self.user.email}: {self.otp_code}"   
    