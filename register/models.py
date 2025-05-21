from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name = 'profile');
    phone = models.CharField(max_length=10,blank=True, null=True);
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    verification_code_created_at = models.DateTimeField(blank=True, null=True)
    def __str__(self):
        return self.user.username;