from django.shortcuts import render
from django.contrib.auth import get_user

# Create your views here.
def landing_page(request):
    user = get_user(request)
    return render(request, "about/about.html", {
        "authenticated": user.is_authenticated,
        "active_page": "about",
        "username": user.get_username()
    })
