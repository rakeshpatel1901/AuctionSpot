from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login as auth_login
from .models import User, UserProfile
import random
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.decorators import login_required
def generate_verification_code():
    return str(random.randint(1000,9999));

def send_verification_email(user_email, verification_code):
    subject = "AUCTION Spot Verification Mail"
    message = f"Your verification code is: {verification_code}"
    from_email = settings.EMAIL_HOST_USER  
    send_mail(subject, message, from_email, [user_email])
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('name')
        password = request.POST.get('password')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        
        
        if password != request.POST.get('confirm_password'):
            messages.error(request,"Password does not match, Try again");
            return render(request,'register.html')
        
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                is_active=False,
            )
            verification_code = generate_verification_code();
            
            user.save()
            profile = UserProfile.objects.create(
                user = user,
                phone=phone,
                verification_code=verification_code,
                verification_code_created_at=timezone.now(),
            )
            request.session['user_email'] = email
            profile.save();
            send_verification_email(user.email,verification_code);
            
            messages.success(request,'Registered Successfully, Please Login')
            return redirect('verify-email/')
        except Exception as e:
            messages.error(request,f"Error during registration : {e}")
            return render(request,'register.html')
        
    return render(request,'register.html');

def verify_email(request):
    if request.method == 'POST':
        verification_code = request.POST.get('verification_code')

        try:
            # Retrieve the email from the session
            user_email = request.session.get('user_email')
            
            if not user_email:
                messages.error(request, "No email found in session.")
                return redirect('register_view')  # Or another appropriate redirect
            
            # Retrieve the user based on the email from the session
            user = User.objects.get(email=user_email)
            profile = user.profile  # Assuming the user has a related profile

            if profile.verification_code == verification_code:
                time_difference = timezone.now() - profile.verification_code_created_at
                if time_difference.total_seconds() > 60:
                    messages.error(request, "The verification code has expired. Please request a new one.")
                    user = User.objects.filter(email = user_email).first()
                    UserProfile.objects.filter(user=user).delete()
                    user.delete()
                    return redirect('register')
                else:
                    user.is_active = True  # Mark user as active after successful verification
                    user.save()
                    del request.session['user_email'];
                    messages.success(request, 'Email verified successfully. Please log in.')
                    return redirect('login')  # Redirect to login page after success    
            else:
                
                messages.error(request, 'Invalid verification code.')

        except Exception as e:
            messages.error(request, f"Error during verification: {e}")

    return render(request, 'verify-email.html')