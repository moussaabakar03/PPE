from django import forms

class ContactForm(forms.Form):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'readonly': 'readonly', 'id': 'id_email'}))

    sujet = forms.CharField(max_length=150, label="Sujet")
    message = forms.CharField(widget=forms.Textarea, label="Message")
