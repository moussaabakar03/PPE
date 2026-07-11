from django import forms

class ContactForm(forms.Form):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'readonly': 'readonly', 'id': 'id_email'}))

    sujet = forms.CharField(max_length=150, label="Sujet")
    message = forms.CharField(widget=forms.Textarea, label="Message")



class FormMessageCommun(forms.Form):
    sujet = forms.CharField(max_length=150, label="Sujet", widget=forms.TextInput(attrs={"class": "form-control"}))
    message = forms.CharField(
    label="Message",
    widget=forms.Textarea(
        attrs={
            "class": "form-control w-100",
            "style": "width:100%; height:100px;",
            "placeholder": "Écrivez votre message ici...",
             "rows": 5,  # hauteur (nb de lignes visibles)
            "cols": 50, # largeur (nb de colonnes visibles)
        }
    )
)

