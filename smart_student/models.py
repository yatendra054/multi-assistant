from django.db import models
from django.contrib.auth.models import User

class Userinformation(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    User_name=models.CharField(max_length=50,blank=True,null=True)
    Email=models.EmailField(null=True,blank=True)
    def __str__(self)->str:
        return self.User_name