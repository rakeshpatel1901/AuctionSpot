from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login as auth_login
from register.models import User

# Create your views here.
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email,password)
        try:
            
            user = authenticate(request, username=email, password=password)
            if user is not None:
            # If the user is found and password is correct, check if the account is active
                if user.is_active:
                    auth_login(request, user)  # Log the user in
                    messages.success(request, f"Welcome {user.username}")
                    request.session['user_email'] = user.email
                    return redirect('../home/')  #
                else:
                    messages.error(request, 'Account is not active')
            else:
                messages.error(request, 'Invalid  or password')
        except User.DoesNotExist:
            messages.error(request, 'Invalid  or password')

    return render(request,'login.html');
