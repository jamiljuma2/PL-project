from django.shortcuts import render

def home(request):
    return render(request, "api_home.html")
