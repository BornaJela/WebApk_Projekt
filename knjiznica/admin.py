from django.contrib import admin
from .models import Autor,Zanr,Knjiga,Profile
admin.site.register(Autor)
admin.site.register(Zanr)
admin.site.register(Knjiga)
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display=['user','je_zaposlenik']
    list_editable=['je_zaposlenik']
