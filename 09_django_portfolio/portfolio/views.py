from django.shortcuts import render,redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Project
from .forms import ContactForm

def home(request):
    return render(request,'portfolio/home.html',{'projects':Project.objects.all()})

@require_http_methods(['GET','POST'])
def contact(request):
    form=ContactForm(request.POST if request.method=='POST' else None)
    if request.method=='POST' and form.is_valid():
        form.save()
        messages.success(request,'Your message was saved to the local portfolio inbox.')
        return redirect('contact')
    return render(request,'portfolio/contact.html',{'form':form})
