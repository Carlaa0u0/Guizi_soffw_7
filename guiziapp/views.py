from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def sobre_nosotros(request):
    return render(request, 'sobre_nosotros.html')

def signup_view(request):
    return render(request, 'signup.html')  # o lo que necesites
