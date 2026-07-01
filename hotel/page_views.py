from django.shortcuts import render


def home(request):
    return render(request, "hotel/index.html")
