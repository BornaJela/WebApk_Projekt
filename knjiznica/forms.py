from django import forms
from .models import Knjiga
class KnjigaForm(forms.ModelForm):
    class Meta:
        model=Knjiga
        fields=['naslov','autor','zanr','godina','opis','kolicina']
        widgeti={
            'opis':forms.Textarea(attrs={'rows':4}),
        }