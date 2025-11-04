from django.shortcuts import render

def home(request):
    """
    網站首頁
    展示系統介紹與功能說明
    """
    return render(request, 'core/home.html')
