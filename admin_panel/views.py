from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from test_app.models import Test, TestAttempt
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
@login_required
def index(request):
    if not (request.user.is_superuser):
        return redirect('accounts:login')
    User = get_user_model()
    return render(request, "admin/adminpanel.html", {"tests": Test.objects.all(), "users": User.objects.all()})
@login_required
def create_test(request):
    if not (request.user.is_superuser):
        return redirect('accounts:login')
    return HttpResponse("eh")
@login_required
def testattempts(request, testid):
    try:
        if not (request.user.is_superuser):
            return redirect('accounts:login')
        test = Test.objects.get(id=testid)
        test_attempts = TestAttempt.objects.filter(test=test)
        return render(request, "admin/test_attempts.html", {"attempts": test_attempts, "test":test})
    except:
        return redirect("test_app:index")
    
@login_required
def userattempts(request, userid):
    try:
        if not (request.user.is_superuser):
            return redirect('accounts:login')
        User = get_user_model()
        user = User.objects.get(id=userid)
        test_attempts = TestAttempt.objects.filter(user=userid)
        return render(request, "admin/user_attempts.html", {"attempts": test_attempts, "user": user})
    except:
        return redirect("test_app:index")
    
@login_required
def delete_test(request, testid):
    try:
        if not (request.user.is_superuser):
            return redirect('accounts:login')
        Test.objects.get(id=testid).delete()
        return redirect("admin_panel:index")
    except:
        return redirect("test_app:index")