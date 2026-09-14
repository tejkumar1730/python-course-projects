from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q,Avg
from django.shortcuts import render,redirect,get_object_or_404
from django.views.decorators.http import require_http_methods
from .models import Student
from .forms import StudentForm
staff_required=user_passes_test(lambda user:user.is_active and user.is_staff)

@staff_required
def home(request):
    query=request.GET.get('q','').strip()
    records=Student.objects.all()
    if query: records=records.filter(Q(name__icontains=query)|Q(roll_number__icontains=query)|Q(course__icontains=query))
    summary=records.aggregate(average=Avg('score'))
    return render(request,'students/home.html',{'page':Paginator(records,10).get_page(request.GET.get('page')),'q':query,'count':records.count(),'average':summary['average']})

@staff_required
@require_http_methods(['GET','POST'])
def edit(request,pk=None):
    student=get_object_or_404(Student,pk=pk) if pk is not None else None
    form=StudentForm(request.POST if request.method=='POST' else None,instance=student)
    if request.method=='POST' and form.is_valid():
        form.save(); messages.success(request,'Student record saved.'); return redirect('home')
    return render(request,'students/form.html',{'form':form,'editing':student is not None})

@staff_required
@require_http_methods(['GET','POST'])
def delete(request,pk):
    student=get_object_or_404(Student,pk=pk)
    if request.method=='POST':
        student.delete(); messages.success(request,'Student record deleted.'); return redirect('home')
    return render(request,'students/delete.html',{'student':student})
