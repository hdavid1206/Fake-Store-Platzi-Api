from django.shortcuts import render

# Create your views here.
def ayuda(request):
    return render(request, 'ayuda.html')