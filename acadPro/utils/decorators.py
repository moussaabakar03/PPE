from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Vous n\'avez pas les droits pour accéder à cette page')
        return redirect('connexion')  
    return wrapper

def staff_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Vous n\'avez pas les droits pour accéder à cette page')
        return redirect('connexion') 
    return wrapper

def eleve_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_staff and not request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        messages.error(request, ' Vous n\'avez pas les droits pour accéder à cette page')
        return redirect('connexion') 
    return wrapper
