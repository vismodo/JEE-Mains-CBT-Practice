from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('login')
        else:
            return render(request, 'accounts/register.html', {'error': form.errors})
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST' and request.POST.get('username') and request.POST.get('password'):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('../')
        else:
            return redirect('../login?badpw=True')

    badpw = request.GET.get('badpw', False)
    return render(request, 'accounts/login.html', {'badpw': badpw})

@login_required
def logout_view(request):
    logout(request)
    return redirect('../')

def index(request):
    if request.user.is_authenticated:
        return redirect('test_app:index')
    else:
        return redirect('accounts:login')