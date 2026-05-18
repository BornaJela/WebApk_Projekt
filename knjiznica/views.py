from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required,user_passes_test
from .models import Knjiga,Autor,Zanr,Posudba
from django.utils import timezone   
from .forms import KnjigaForm
from django.db.models import Sum,Count
def popis_knjiga(request):
    knjige=Knjiga.objects.all()
    autori=Autor.objects.all()
    zanrovi=Zanr.objects.all()
    autor_id=request.GET.get('autor')
    if autor_id:
        knjige=knjige.filter(autor_id=autor_id)
    zanr_id=request.GET.get('zanr')
    if zanr_id:
        knjige=knjige.filter(zanr_id=zanr_id)
    stanje=request.GET.get('stanje')
    if stanje=='dostupno':
        knjige=knjige.exclude(kolicina=0)
    return render(request,'knjiznica/popis_knjiga.html',{
        'knjige':knjige,
        'autori':autori,
        'zanrovi':zanrovi,
        'trenutni_autor':autor_id,
        'trenutni_zanr':zanr_id,
        'trenutno_stanje':stanje,
    })
def registracija(request):
    if request.method=='POST':
        form=UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form=UserCreationForm()
    return render(request,'knjiznica/registracija.html',{'form':form})
def is_admin(user):
    return user.is_staff
@login_required
@user_passes_test(is_admin)
def dodaj_knjigu(request):
    if request.method=='POST':
        form=KnjigaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('popis_knjiga')
    else:
        form=KnjigaForm()
    return render(request,'knjiznica/dodaj_knjigu.html',{'form':form})

@login_required
@user_passes_test(is_admin)
def uredi_knjigu(request,id):
    knjiga=get_object_or_404(Knjiga,id=id)
    if request.method=='POST':
        form=KnjigaForm(request.POST,instance=knjiga)
        if form.is_valid():
            form.save()
            return redirect('popis_knjiga')
    else:
        form=KnjigaForm(instance=knjiga)
    return render(request,'knjiznica/uredi_knjigu.html',{'form':form,'knjiga':knjiga})

@login_required
@user_passes_test(is_admin)
def obrisi_knjigu(request,id):
    knjiga=get_object_or_404(Knjiga,id=id)
    if request.method=='POST':
        knjiga.delete()
        return redirect('popis_knjiga')
    return render(request,'knjiznica/obrisi_knjigu.html',{'knjiga':knjiga})
@login_required
def posudi_knjigu(request,id):
    knjiga=get_object_or_404(Knjiga,id=id)
    if knjiga.kolicina>0:
        knjiga.kolicina-=1
        knjiga.puta_posudjena+=1
        knjiga.save()

        Posudba.objects.create(
            knjiga=knjiga,
            korisnik=request.user
        )
    return redirect('popis_knjiga')
@login_required
def vrati_knjigu(request,id):
    posudba=get_object_or_404(Posudba,id=id,korisnik=request.user,je_vraceno=False)
    posudba.je_vraceno=True
    posudba.datum_povrata=timezone.now()
    posudba.save()
    knjiga=posudba.knjiga
    knjiga.kolicina+=1      
    knjiga.save()
    return redirect('moje_posudbe')
@login_required
def moje_posudbe(request):
    aktivne_posudbe=Posudba.objects.filter(
        korisnik=request.user,
        je_vraceno=False
    ).select_related('knjiga')
    povijest_posudbi=Posudba.objects.filter(
        korisnik=request.user,
        je_vraceno=True
    ).select_related('knjiga')[:20]
    return render(request,'knjiznica/moje_posudbe.html',{
        'aktivne_posudbe':aktivne_posudbe,'povijest_posudbi':povijest_posudbi,
    })
def is_zaposlenik(user):
    return user.is_authenticated and (
        user.is_staff or
        (hasattr(user,'profile') and user.profile.je_zaposlenik))
@login_required
@user_passes_test(is_zaposlenik)
def statistika(request):
    najposudjenije=Knjiga.objects.order_by('-puta_posudjena')[:3]
    najpopularniji_autori=Autor.objects.annotate(
        ukupno_posudbi=Sum('knjiga__puta_posudjena')).order_by('-ukupno_posudbi')[:3]
    ukupno_knjiga=Knjiga.objects.count()
    rezultat=Knjiga.objects.aggregate(Sum('puta_posudjena'))
    ukupno_posudbi=rezultat['puta_posudjena__sum'] or 0
    trenutno_posudjeno=Posudba.objects.filter(je_vraceno=False).count()
    context={
        'najposudjenije':najposudjenije,
        'najpopularniji_autori':najpopularniji_autori,
        'ukupno_knjiga':ukupno_knjiga,
        'ukupno_posudbi': ukupno_posudbi,
        'trenutno_posudjeno': trenutno_posudjeno,
    }
    return render(request,'knjiznica/statistika.html',context)