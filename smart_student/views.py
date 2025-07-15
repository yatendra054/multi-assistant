from django.shortcuts import render,redirect
from django.contrib import messages 
import re
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from .models import*
from smart_student.assitant import handle_llm_model
import json


def smart(request):

    if request.method == "POST" and "password_key" in request.POST:
      
        request.session["groq_api_key"] = request.POST["password_key"]
    
        return redirect("smart")

    api_key = request.session.get("groq_api_key")
    if request.method == "POST" and request.POST.get("action") == "logout":
        request.session.pop("groq_api_key", None)
        request.session.pop("chat_history", None)
        return redirect("smart")

    context = handle_llm_model(request, api_key)
    context["chat_history"] = request.session.get("chat_history", [])
    return render(request, "index.html", context)



def clear_chat(request):
    request.session['chat_history'] = []
    return redirect("smart")

def login_page(request):
    if request.method == "POST":
        data = request.POST
        username = data.get("username")
        password = data.get("password")
        email = data.get("email")

   
        if not re.match(r"[a-zA-Z0-9._%+-]+@(gmail|yahoo)\.com", email):
            messages.warning(request, "Email invalid format")
            return redirect('login_page')

        if len(password) < 8:
            messages.warning(request, "Password should be at least 8 characters")
            return redirect('login_page')

        user_by_name = User.objects.filter(username=username).first()
        user_by_email=User.objects.filter(email=email).first()
        
        if user_by_name:
            
            user_auth = authenticate(request, username=username, password=password)
            if user_auth:
                login(request, user_auth)
                messages.info(request, "Welcome back!")
                return redirect('/smart')
            else:
                messages.warning(request, "Incorrect password.")
                return redirect('login_page')
        if user_by_email:
            
            messages.warning(request,"Email is already registered Try with another")
            return redirect('login_page')  
         
            
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        user_info=Userinformation.objects.create(
            user=user,
            User_name=username,
            Email=email
        )
        print(user_info)

        messages.success(request, "User successfully registered.")
        login(request, user)  
        return redirect('/smart')

    return render(request, "login.html")



def logout_page(request):
    logout(request)
    return redirect('login_page')