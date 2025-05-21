from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
def logout_view(request):
    if 'user_email' in request.session:
        user = User.objects.get(email=request.session['user_email'])
        user.is_active = False
        del request.session['user_email']    
    return redirect('home')
    
