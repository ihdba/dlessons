from django.shortcuts import render

# Create your views here.


def dashboard(request):
    
    ctx = {
        'title': "Dashboard",
    }
    
    return render(
        request,
        'dashboard/main.html',
        ctx
    )
    
def about(request):
    
    return render(request, 'dashboard/about.html', {'title': 'About'})