from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.urls import reverse



# def seConnecter(request):
#     return render(request, 'accueil/connexion.html')

def traitement_login(request):
    if request.method == "POST":
        username = request.POST.get("matricule")
        password = request.POST.get("nom")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)
            if user.is_superuser:
                return redirect(reverse('secretaire:index'))
            elif user.groups.filter(name="Eleve").exists():
                return redirect('inscriptionPayement')
        else:
            return redirect('eleve:notes', matricule = username)

    return render(request, 'connexion.html')