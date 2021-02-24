from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import authenticate
from users.models import MyUser
from django.contrib.auth import get_user, logout, login
from django.http import HttpResponseForbidden


def sign_up_user(request):
    if request.method == "POST":
        form = UserCreationForm(request)
        if request.POST["password1"] == request.POST["password2"]:
            user = MyUser.objects.create_user(
                username=request.POST["username"],
                password=request.POST["password1"],
                email=request.POST["email"],
                discord_tag=request.POST["discord_tag"])
            user.save()
            #messages.success(request, "Account created successfully.")
            return redirect("sign_in_user")
    else:
        form = UserCreationForm()

    return render(request, "users/sign_up_user.html", {
        "form": form,
        "authenticated": False,
        "active_page": "sign_up"
    })


def sign_in_user(request):
    user = authenticate(username=request.POST.get("username"),
                        password=request.POST.get("password"))
    # Signing in
    if request.method == "POST":
        # User authenticated
        if user:
            login(request, user)
            return render(request, "users/signed_in.html", {
                "username": user.get_username(),
                "authenticated": user.is_authenticated,
                "active_page": "sign_in"})
        else:
            return render(request, "users/sign_in.html",
                          {"form": AuthenticationForm(),
                           "error": "Invalid username or password.",
                           "authenticated": user,
                           "active_page": "sign_in"})

    else:
        return render(request, "users/sign_in.html",
                      {"form": AuthenticationForm(),
                       "authenticated": user,
                       "active_page": "sign_in"})


def sign_out_user(request):
    logout(request)
    user = get_user(request)
    return render(request, "users/sign_out.html",
                  {"authenticated": user.is_authenticated,
                   "active_page": None})


def edit_user(request):

    def update_context(request, context):
        return context | {
            "discord_tag": request.POST["discord_tag"],
            "lifx_dev_token": request.POST["lifx_dev_token"]
        }

    user = get_user(request)
    my_user = MyUser.objects.filter(username=user.get_username()).first()
    context = {
        "authenticated": user.is_authenticated,
        "active_page": "edit_user",
        "username": user.get_username(),
        "discord_tag": my_user.discord_tag,
        "lifx_dev_token": my_user.lifx_dev_token
    }

    if request.method == "GET" and user.is_authenticated:
        return render(request, "users/edit_user.html", context)

    # POST & is authenticated & got password right.
    elif (request.method == "POST" and
          user.is_authenticated and
          user.check_password(request.POST.get("current_password"))):
        my_user = MyUser.objects.filter(username=user.get_username()).first()
        my_user.discord_tag = request.POST["discord_tag"]
        my_user.lifx_dev_token = request.POST["lifx_dev_token"]

        # User updates their password.
        if (request.POST["password1"] and
                request.POST["password1"] == request.POST["password2"]):
            user.set_password(request.POST["password1"])

        # New passwords do not match.
        elif (request.POST["password1"] or request.POST["password2"] and
                request.POST["password1"] != request.POST["password2"]):
            return render(request, "users/edit_user.html", context | {
                "error": "Can't change password: New passwords do not match."
            })

        my_user.save()
        user.save()
        return render(request, "users/edit_user.html",
                      update_context(request, context | {"saved": True}))
    # Not logged in, can't be allowed on to this page.
    else:
        return render(request, "users/wrong_pw_or_unauthenticated.html",
                      {"authenticated": user.is_authenticated})
