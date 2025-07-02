from django import forms
from django.contrib.auth import authenticate

class ConnexionForm(forms.Form):
    identifiant = forms.CharField(
        label='Email ou Username * :',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'id': 'login-password', 'placeholder': 'Votre mot de passe', 'required': 'required'})
    )

    def clean(self):
        cleaned_data = super().clean()
        identifiant = cleaned_data.get('identifiant')
        password = cleaned_data.get('password')

        user = authenticate(username=identifiant, password=password)
        if user is None:
            raise forms.ValidationError("Identifiant ou mot de passe incorrect.")
        if not user.is_active:
            raise forms.ValidationError("Ce compte est désactivé.")

        cleaned_data['user'] = user
        return cleaned_data

    def get_user(self):
        return self.cleaned_data.get('user')



class ContactForm(forms.Form):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'readonly': 'readonly', 'id': 'id_email'}))

    sujet = forms.CharField(max_length=150, label="Sujet")
    message = forms.CharField(widget=forms.Textarea, label="Message")
